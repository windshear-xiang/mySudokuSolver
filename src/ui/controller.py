"""控制器层

其实更接近 MVP 的 Presenter 不过我们还是叫它控制层吧。

所有和 ui 界面逻辑相关的逻辑都放在这里，而需要操作数据的内容都放在 model 层。
调用求解器需要多线程，所以放在控制层，这是一个例外。

控制器会不断读取 model 层的数据，然后传参调用 view 层去显示。
"""

import tkinter as tk
from tkinter import filedialog
import queue
import threading
import time
from src.ui.model import SudokuModel
from src.ui.view import SudokuView
from src.solver.sudoku import Sudoku

REFRESH_TIME_INTERVAL = 100

class SudokuController:
    def __init__(self, puzzle_board, constraints) -> None:
        
        # 视图层
        self.view = SudokuView()
        self.raw_logger = self.view.raw_logger # 从视图层构造日志生成器

        # 模型层
        self.model = SudokuModel(puzzle_board, constraints, self.raw_logger("model"))

        # 控制层自用的日志生成器
        self.log = self.raw_logger("controller")

        # 控制层状态属性
        self.solving = False # 正在求解
        self.selected_cell = None # 当前选中的格子 (i, j)
        self.auto_solve_var = tk.BooleanVar(value=False) # 自动求解模式

        # 求解线程通讯等
        self.solver_thread: threading.Thread | None = None # 求解线程
        self.out_q = queue.Queue()
        self.stop_event = threading.Event()

        # 绑定处理函数
        self._bind_events()

        # 初始刷新界面
        self.view.root.after(REFRESH_TIME_INTERVAL, self.check_update)
        self.on_refresh_constraints()
    
    def _bind_events(self):
        """注册视图层事件到控制层处理函数"""
        self.view.bind_event("cell_click", self.on_cell_click)
        self.view.bind_event("start_solver", self.on_start_solver)
        self.view.bind_event("stop_solver", self.on_stop_solver)
        self.view.bind_event("save", self.on_save)
        self.view.bind_event("load", self.on_load)
        self.view.bind_event("undo", self.on_undo)
        self.view.bind_event("redo", self.on_redo)
        self.view.bind_event("delete_constraint", self.on_delete_constraint)
        # 绑定键盘事件（全局绑定，编辑状态下处理数字和删除操作）
        self.view.root.bind("<Key>", self.on_key_pressed)
        # 自动求解勾选框，勾选的时候也会自动求解一次
        self.view.auto_solve_cb.config(variable=self.auto_solve_var, command=self._auto_start_solver)
    
    def check_update(self):
        self.view.update_display(self.model.curr_puzzle_board,
                                 self.model.curr_tuf_board,
                                 self.model.constraints,
                                 self.selected_cell)
        self.listen_solver()
        self.view.root.after(REFRESH_TIME_INTERVAL, self.check_update)

    def on_refresh_constraints(self):
        """假装存在一个按钮叫：刷新 constraints 显示列表"""
        self.view.refresh_constraints_panel(self.model.constraints)
    
    def on_delete_constraint(self, index):
        if self.solving:
            self.log("目前在求解中，不能删除 constraint")
            return
        if self.model.del_constraint(index):
            self.on_refresh_constraints()
            self._auto_start_solver()
        return

    def on_save(self):
        if self.solving:
            self.log("目前在求解中，不能保存")
            return
        self.log("试图储存当前棋盘")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Save Current Sudoku"
        )
        if not file_path:
            self.log("用户取消储存操作")
            return
        # 保存数据到文件中
        try:
            self.model.save_to_file(file_path)
        except Exception as e:
            self.log(str(e))
            self.log("保存失败")
        else:
            self.log("棋盘已保存到 " + file_path)

    def on_load(self):
        if self.solving:
            self.log("目前在求解中，不能读取")
            return
        self.log("试图读取棋盘")
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Load Current Sudoku"
        )
        if not file_path:
            self.log("用户取消读取操作")
            return
        # 读取文件中的数据
        try:
            self.model.load_from_file(file_path)
        except Exception as e:
            self.log("" + str(e))
            self.log("读取失败")
        else:
            self.log("已读取 " + file_path)
            self.on_refresh_constraints()
        
    def on_undo(self):
        if self.solving:
            self.log("目前在求解中，不能撤销操作")
            return
        if self.model.to_prev_history():
            self.on_refresh_constraints()
            self._auto_start_solver()

    def on_redo(self):
        if self.solving:
            self.log("目前在求解中，不能恢复操作")
            return
        if self.model.to_next_history():
            self.on_refresh_constraints()
            self._auto_start_solver()
    
    def on_cell_click(self, i: int, j: int):
        self.selected_cell = (i, j)       
    
    def on_key_pressed(self, event):
        if self.solving and not self.auto_solve_var.get():
            self.log("目前在求解中，不能修改棋盘")
            return
        if self.selected_cell is None:
            return
        i, j = self.selected_cell
        if len(event.char) == 1 and event.char.isdigit() and event.char != '0':
            # 如果按下数字键1~9，则设定该格的值，并标记为用户输入
            digit = int(event.char)
            if self.model.set_digit(i, j, digit):
                self._auto_start_solver()
        elif event.keysym in ("BackSpace", "Delete"):
            # 清空当前格（置为0）
            if self.model.del_digit(i, j):
                self._auto_start_solver()
    
    def _auto_start_solver(self):
        if self.auto_solve_var.get():
            if self.solving:
                self.log("目前在求解中，将中止并重新求解")
                self.on_stop_solver()
                self.view.root.after(REFRESH_TIME_INTERVAL, self._auto_start_solver)
                return
            self.on_start_solver()
        
    def on_start_solver(self):
        """启动求解器"""
        if self.solving:
            self.log("目前已经在求解中，不能重复启动")
            return
        self.solving = True
        self.stop_event.clear()
        # 构造数独对象
        s = Sudoku(
            self.model.curr_puzzle_board,
            self.model.constraints,
            self.out_q,
            self.stop_event
            )
        # 启动求解线程
        self.log("启动求解线程...")
        self.solver_thread = threading.Thread(target=worker, args=(s, self.raw_logger("solver")), daemon=True)
        self.solver_thread.start()
    
    def on_stop_solver(self):
        self.log("试图停止求解线程...")
        self.stop_event.set()
    
    def listen_solver(self):
        """检查 out_q 里有没有收到中间结果，这个函数不会自己循环，需要不断被调用"""
        try:
            # 取出队列里的所有数据
            while True:
                out = self.out_q.get_nowait()
                if out is None:
                    # 求解结束
                    self.solving = False
                    self.log("接收到求解结束讯息")
                else:
                    self.log("接收到中间结果")
                    self.model.curr_tuf_board = out
        except queue.Empty:
            pass
        except Exception as e:
            self.log(str(e))
        return

def worker(s: Sudoku, log):
    """运行在另一个线程"""
    log("求解线程被调用")
    assert s.out_q is not None
    try:
        for i, constraint in enumerate(s.constraints):
            if not getattr(constraint, "preprocessed_flag", True):
                log(f"需要预处理 C{i}:{type(constraint).__name__}")
                prep_timer = time.perf_counter()
                getattr(constraint, "preprocess").__call__()
                setattr(constraint, "preprocessed_flag", True)
                log(f"C{i} 预处理完成. {time.perf_counter() - prep_timer:.3f}s")
        log("开始求解")
        s.solve_true_candidates()
    except InterruptedError:
        log("求解已被中止")
    except Exception as e:
        log(str(e))
    else:
        s.out_q.put(s.tuf_board.copy())
        sc, ct = s.get_counter_stat()
        log(f"求解完成. {sc}steps {ct:.3f}s")
    finally:
        s.out_q.put(None)

