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
from src.constraints import CONSTRAINT_CLASSES_LIST
from src.utils.check_conflict import has_conflict

REFRESH_TIME_INTERVAL = 100

class SudokuController:
    def __init__(self, puzzle_board, constraints) -> None:

        # 可用的 constraints 有哪些
        self.constraints_dict = {
            ConstraintClass.__name__: ConstraintClass
                for ConstraintClass in CONSTRAINT_CLASSES_LIST
        }
        
        # 视图层
        self.view = SudokuView(list(self.constraints_dict.keys()))
        self.raw_logger = self.view.raw_logger # 从视图层构造日志生成器

        # 模型层
        self.model = SudokuModel(puzzle_board, constraints, self.raw_logger("model"))

        # 控制层自用的日志生成器
        self.log = self.raw_logger("controller")

        # 控制层状态属性 - 求解相关
        self.solving: bool = False # 正在求解
        self.selected_cell: tuple[int, int] | None = None # 当前选中的格子 (i, j)
        self.auto_solve_var = tk.BooleanVar(value=False) # 自动求解模式

        # 控制层状态属性 - 限制规则相关
        self.config_constraint: bool = False # 正在设置限制规则
        self.config_constraint_index: int | None = None # 在设置的限制规则的编号
        # 这俩不用的时候记得清零
        self.temp_constraint_cells: list = []
        self.temp_constraint_params: dict[str, tk.Variable] = {}

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
        self.view.bind_event("left_cell_click", self.on_left_cell_click)
        self.view.bind_event("right_cell_click", self.on_right_cell_click)
        self.view.bind_event("start_solver", self.on_start_solver)
        self.view.bind_event("stop_solver", self.on_stop_solver)
        self.view.bind_event("save", self.on_save)
        self.view.bind_event("load", self.on_load)
        self.view.bind_event("undo", self.on_undo)
        self.view.bind_event("redo", self.on_redo)
        self.view.bind_event("clear_results", self.on_clear_results)
        self.view.bind_event("delete_constraint", self.on_delete_constraint)
        self.view.bind_event("new_constraint", self.on_new_constraint)
        self.view.bind_event("enter_config_constraint", self.on_enter_config_constraint)
        self.view.bind_event("exit_config_constraint", self.on_exit_config_constraint)
        self.view.bind_event("confirm_config_constraint", self.on_confirm_config_constraint)
        # 绑定键盘事件（全局绑定，编辑状态下处理数字和删除操作）
        self.view.root.bind("<Key>", self.on_key_pressed)
        self.view.root.bind("<Control-z>", lambda _: self.on_undo())
        self.view.root.bind("<Control-y>", lambda _: self.on_redo())
        self.view.root.bind("<Control-s>", lambda _: self.on_save())
        self.view.root.bind("<Control-o>", lambda _: self.on_load())
        # 自动求解勾选框，勾选的时候也会自动求解一次
        self.view.auto_solve_cb.config(variable=self.auto_solve_var, command=self._auto_start_solver)
        self.view.display_color_cb.config(command=self.on_refresh_constraints)
    
    def check_update(self):
        self.view.update_display(
            self.model.curr_puzzle_board,
            self.model.curr_tuf_board,
            self.model.constraints,
            self.selected_cell,
            self.temp_constraint_cells,
            self.config_constraint_index
        )
        self.listen_solver()
        self.view.root.after(REFRESH_TIME_INTERVAL, self.check_update)

    def on_left_cell_click(self, i: int, j: int):
        if self.config_constraint:
            # 目前正在修改constraint状态
            self.selected_cell = None
            if (i, j) not in self.temp_constraint_cells:
                self.temp_constraint_cells.append((i, j))
        else:
            # 目前正在普通状态
            self.selected_cell = (i, j)
        return
    
    def on_right_cell_click(self, i: int, j: int):
        if self.config_constraint:
            # 目前正在修改constraint状态
            if (i, j) in self.temp_constraint_cells:
                self.temp_constraint_cells.remove((i, j))
        return

    def on_new_constraint(self, constraint_name: str):
        if self.solving:
            self.log("求解中，不能新建限制规则")
            return
        if self.config_constraint:
            self.log("正在修改限制规则，请先确认或取消")
            return
        ConstraintClass = self.constraints_dict[constraint_name]
        self.model.add_constraint(ConstraintClass)
        return self.on_refresh_constraints()

    def on_enter_config_constraint(self, index):
        """进入 config constraint 的模式"""

        if self.solving:
            self.log("求解中，不能修改限制规则")
            return
        if self.config_constraint:
            self.log("正在修改限制规则，请先确认或取消")
            return

        # 这一步模型层会检查能不能找到这个constraint
        c_params = self.model.get_constraint_params(index)
        if c_params is None:
            return

        # 进入config模式，会禁用按键、改变click逻辑等等
        self.log("进入 config constraint 模式")
        self.config_constraint = True
        self.config_constraint_index = index
        self.selected_cell = None

        # 从model获取临时的cells和params
        self.temp_constraint_cells = self.model.get_constraint_cells(index)
        self.temp_constraint_params = {
            key: tk.Variable(value=value) for key, value in c_params.items()
        }

        return self.on_refresh_constraints()

    def on_exit_config_constraint(self):
        """退出 config constraint 的模式"""
        
        # 全部恢复原样
        self.log("退出 config constraint 模式")
        self.config_constraint = False
        self.config_constraint_index = None
        self.temp_constraint_cells = []
        self.temp_constraint_params = {}

        return self.on_refresh_constraints()

    def on_confirm_config_constraint(self):
        """在进入了 config constraint 的模式之后，确认修改"""
        c_params = {key: var.get() for key, var in self.temp_constraint_params.items()}
        succ = self.model.config_constraint(
            self.temp_constraint_cells,
            c_params,
            self.config_constraint_index
        )
        if succ:
            self.on_exit_config_constraint()
            self._auto_start_solver()
        return

    def on_refresh_constraints(self):
        """假装存在一个按钮叫：刷新 constraints 显示列表"""

        c_dicts = []
        for index, constraint in enumerate(self.model.constraints):
            c_dict = {}
            c_dict["name"] = constraint.__class__.__name__
            c_dict["info"] = constraint.info
            if index == self.config_constraint_index:
                c_dict["params"] = self.temp_constraint_params
            c_dicts.append(c_dict)

        self.view.refresh_constraints_panel(
            c_dicts,
            self.config_constraint_index
        )
    
    def on_delete_constraint(self, index):
        if self.solving:
            self.log("求解中，不能删除限制规则")
            return
        if self.config_constraint:
            self.log("正在修改限制规则，请先确认或取消")
            return
        if self.model.del_constraint(index):
            self.on_refresh_constraints()
            self._auto_start_solver()
        return

    def on_clear_results(self):
        return self.model.clear_results()

    def on_save(self):
        if self.solving:
            self.log("求解中，不能保存存档")
            return
        if self.config_constraint:
            self.log("正在修改限制规则，不能保存存档")
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
            self.log("求解中，不能读取存档")
            return
        if self.config_constraint:
            self.log("目前正在修改限制规则，不能读取存档")
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
            self.log("求解中，不能撤销操作")
            return
        if self.config_constraint:
            self.log("目前正在修改限制规则，不能撤销操作")
            return
        
        if self.model.to_prev_history():
            self.on_refresh_constraints()
            self._auto_start_solver()

    def on_redo(self):
        if self.solving:
            self.log("求解中，不能恢复操作")
            return
        if self.config_constraint:
            self.log("目前正在修改限制规则，不能恢复操作")
            return
        
        if self.model.to_next_history():
            self.on_refresh_constraints()
            self._auto_start_solver()
    
    def on_key_pressed(self, event: tk.Event):
        """和棋盘有关的键盘操作，包括增删数字、移动光标等"""
        if self.selected_cell is None:
            return
        i, j = self.selected_cell

        # 如果按下数字键1~9，则设定该格的值，并标记为用户输入
        if len(event.char) == 1 and event.char.isdigit() and event.char != '0':
            if self.solving and not self.auto_solve_var.get():
                self.log("求解中，不能修改棋盘")
                return
            digit = int(event.char)
            if self.model.set_digit(i, j, digit):
                self._auto_start_solver()
        # 删除数字，清空当前格（置为0）
        elif event.keysym in ("BackSpace", "Delete"):
            if self.solving and not self.auto_solve_var.get():
                self.log("求解中，不能修改棋盘")
                return
            if self.model.del_digit(i, j):
                self._auto_start_solver()
        # 方向键
        elif event.keysym == "Up" and i > 0:
            self.selected_cell = (i-1, j)
        elif event.keysym == "Down" and i < 8:
            self.selected_cell = (i+1, j)
        elif event.keysym == "Left" and j > 0:
            self.selected_cell = (i, j-1)
        elif event.keysym == "Right" and j < 8:
            self.selected_cell = (i, j+1)
    
    def _auto_start_solver(self):
        """可能需要自动求解的时候都调用它，它会自己判断目前是否是自动求解模式，以及目前是否正在求解"""
        if self.config_constraint:
            return
        if self.auto_solve_var.get():
            if self.solving:
                if not self.stop_event.is_set():
                    self.log("求解中，将中止并重新求解")
                    self.on_stop_solver()
                self.view.root.after(REFRESH_TIME_INTERVAL, self._auto_start_solver)
                return
            self.on_start_solver()
        
    def on_start_solver(self):
        """启动求解器"""
        if self.solving:
            self.log("已经在求解中，不能重复启动")
            return
        if self.config_constraint:
            self.log("目前正在修改限制规则，不能求解")
            return
        if has_conflict(self.model.curr_puzzle_board):
            self.log("当前数独有冲突，不能求解")
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
        """强行停止求解器"""
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
                    self.log("接收到结束讯息，求解已结束")
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
        sc, ct = s.get_counter_stat()
        log(f"求解已被中止. {sc}steps {ct:.3f}s")
    except Exception as e:
        log(str(e))
    else:
        s.out_q.put(s.tuf_board.copy())
        sc, ct = s.get_counter_stat()
        log(f"求解完成. {sc}steps {ct:.3f}s")
    finally:
        s.out_q.put(None)

