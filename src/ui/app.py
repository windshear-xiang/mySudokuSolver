import tkinter as tk
import numpy as np
import threading
import queue
import time
from src.solver import Sudoku
from src.constraints import *

REFRESH_TIME_INTERVAL = 100

class SudokuUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Sudoku Solver")

        # 状态属性
        self.solving = False # 求解状态
        self.editable = True # 棋盘可编辑状态
        self.selected_cell = None # 当前选中的格子 (i, j)
        self.always_solve_var = tk.BooleanVar(value=False) # 自动求解模式

        # 当前显示的棋盘
        self.curr_puzzle_board = np.zeros((9, 9), dtype=np.int8)
        self.curr_tuf_board = np.zeros((9, 9, 9), dtype=np.int8)

        # Constraints
        self.constraint = []

        # 多线程工具
        self.out_q = queue.Queue()
        self.stop_event = threading.Event()

        # 创建9x9网格（存放各格 Canvas）
        self.cells: list[list[tk.Canvas]] = [[None for _ in range(9)] for _ in range(9)] # type: ignore
        for i in range(9):
            for j in range(9):
                canvas = tk.Canvas(self.root, width=90, height=90, 
                                     highlightthickness=0, bg='white')
                canvas.grid(row=i, column=j, padx=0, pady=0)
                # 绘制单元格边框
                self._draw_cell_borders(canvas, i, j)
                # 绑定点击事件（仅在编辑状态下有效）
                canvas.bind("<Button-1>", lambda e, i=i, j=j: self.select_cell(i, j))
                self.cells[i][j] = canvas

        # 右侧面板：包含 Solve 按钮和日志显示框
        self.side_frame = tk.Frame(self.root)
        self.side_frame.grid(row=0, column=9, rowspan=9, padx=10, pady=10, sticky="n")

        # 在 side_frame 顶部创建一个控制区（control_frame）用于放置勾选框和按钮
        self.control_frame = tk.Frame(self.side_frame)
        self.control_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

        # 添加 “Always Solve” 勾选框，放在第一列
        self.always_solve_cb = tk.Checkbutton(self.control_frame, text="Always Solve", variable=self.always_solve_var)
        self.always_solve_cb.grid(row=0, column=0, padx=5)

        # 修改原来 True Candidates 按钮
        self.solve_button = tk.Button(self.control_frame, text="True Candidates", command=self.start_solver)
        self.solve_button.grid(row=0, column=1, padx=5)

        # 在 True Candidates 按钮右边新增 Stop 按钮（先不绑定功能，预留接口）
        self.stop_button = tk.Button(self.control_frame, text="Stop", command=self.stop_solver)
        self.stop_button.grid(row=0, column=2, padx=5)

        # 日志显示框（用于显示文字信息）
        self.log_text = tk.Text(self.side_frame, width=35, height=30, state=tk.NORMAL)
        self.log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 新增 constraints 显示框，放在日志显示框下面
        self.constraint_text = tk.Text(self.side_frame, width=35, height=10, state=tk.DISABLED)
        self.constraint_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 绑定键盘事件（全局绑定，编辑状态下处理数字和删除操作）
        self.root.bind("<Key>", self.on_key_pressed)
        
        # 初始刷新界面
        self.root.after(REFRESH_TIME_INTERVAL, self.check_update)
    
    def _draw_cell_borders(self, canvas, i, j):
        # 清除并重绘单元格边框
        canvas.delete('all')
        
        # 绘制细边线
        canvas.create_line(0, 0, 0, 90, width=1, fill='#cccccc')
        canvas.create_line(0, 0, 90, 0, width=1, fill='#cccccc')
        canvas.create_line(89, 0, 89, 90, width=1, fill='#cccccc')
        canvas.create_line(0, 89, 90, 89, width=1, fill='#cccccc')
        
        # 绘制粗边线
        if j % 3 == 0:
            canvas.create_line(0, 0, 0, 90, width=2)
        if i % 3 == 0:
            canvas.create_line(0, 0, 90, 0, width=2)
        if j % 3 == 2:
            canvas.create_line(89, 0, 89, 90, width=2)
        if i % 3 == 2:
            canvas.create_line(0, 89, 90, 89, width=2)
    
    def _highlight_cell(self, canvas):
        # 绘制红色选中框
        canvas.create_rectangle(2, 2, 88, 88, outline="red", width=3)
    
    def select_cell(self, i, j):
        self.selected_cell = (i, j)
    
    def auto_solve(self):
        if self.always_solve_var.get() == True:
            self.start_solver()
        else:
            pass

    def on_key_pressed(self, event):
        if not self.editable:
            return
        if self.selected_cell is None:
            return
        
        i, j = self.selected_cell
        # 如果按下数字键1~9，则设定该格的值，并标记为用户输入
        if len(event.char) == 1 and event.char.isdigit() and event.char != '0':
            digit = int(event.char)
            if self.curr_puzzle_board[i, j] != digit:
                self.after_add()
                if self.curr_puzzle_board[i, j] != 0:
                    self.after_del()
                self.curr_puzzle_board[i, j] = digit
                self.auto_solve()
        elif event.keysym in ("BackSpace", "Delete"):
            # 清空当前格（置为0）
            if self.curr_puzzle_board[i, j] != 0:
                self.after_del()
                self.curr_puzzle_board[i, j] = 0
                self.auto_solve()

    def after_add(self):
        '''加入新的数字/constraint之后，之前正确的可能错，但是之前错的肯定还错'''
        self.curr_tuf_board[self.curr_tuf_board == 1] = 0
    
    def after_del(self):
        '''删除已有的数字/constraint之后，之前正确的还正确，但是之前错的可能对'''
        self.curr_tuf_board[self.curr_tuf_board == -1] = 0

    def check_update(self):
        # 每隔0.1秒读取一次结果，刷新界面显示
        try:
            # 取出队列里的所有数据
            while True:
                out = self.out_q.get_nowait()
                if out is None:
                    # 求解结束
                    self.log("[main]: 接收到求解结束讯息")
                    self.solving = False
                    self.editable = True
                else:
                    self.log("[main]: 接收到求解中间结果")
                    self.curr_tuf_board = out
        except queue.Empty:
            pass
        finally:
            self.update_display()
            self.root.after(REFRESH_TIME_INTERVAL, self.check_update)
    
    def update_display(self):
        for i in range(9):
            for j in range(9):
                canvas = self.cells[i][j]
                canvas.delete('all')
                self._draw_cell_borders(canvas, i, j)
                if self.curr_puzzle_board[i, j] != 0:
                    self._draw_assigned_number(canvas, self.curr_puzzle_board[i, j])
                else:
                    cell_data = self.curr_tuf_board[i, j]
                    true_cand_count = np.sum(cell_data == 1)
                    false_cand_count = np.sum(cell_data == -1)
                    if true_cand_count == 1 and false_cand_count == 8:
                        # 已确定的格子：画大数字
                        num = int(np.argmax(cell_data) + 1)
                        self._draw_big_number(canvas, num)
                    else:
                        # 未确定：绘制候选信息
                        self._draw_small_grid(canvas, cell_data)
                if self.selected_cell == (i, j):
                    self._highlight_cell(canvas)
    
    def _draw_assigned_number(self, canvas: tk.Canvas, number: int):
        canvas.create_text(45, 45, text=str(number), font=('Arial', 40), fill='black')
    
    def _draw_big_number(self, canvas: tk.Canvas, number: int):
        canvas.create_text(45, 45, text=str(number), font=('Arial', 40), fill='blue')
        
    def _draw_small_grid(self, canvas: tk.Canvas, cell_data: np.ndarray):
        # 无解情况
        if np.all(cell_data == -1):
            return
        for num in range(1, 10):
            idx = num - 1
            state = cell_data[idx]
            row = (num - 1) // 3
            col = (num - 1) % 3
            x = col * 30 + 15
            y = row * 30 + 15
            if state == -1:
                color = 'white'
            elif state == 1:
                color = 'blue'
            else:
                color = '#cccccc'
            canvas.create_text(x, y, text=str(num), font=('Arial', 10), fill=color)
    
    def stop_solver(self):
        self.log("[main]: 试图停止求解器")
        self.stop_event.set()

    def start_solver(self):
        if self.solving == True:
            self.log("[main]: 正在求解，请稍等")
            return
        
        self.solving = True
        self.editable = False
        self.stop_event.clear()
        # 构造数独对象
        s = Sudoku(
            self.curr_puzzle_board,
            self.constraint,
            self.out_q,
            self.stop_event
            )
        # s.tuf_board = self.curr_tuf_board.copy()
        # 启动求解线程
        solver_thread = threading.Thread(target=self.worker, args=(s,), daemon=True)
        solver_thread.start()

    def worker(self, s: Sudoku):
        self.log("[worker]: worker被调用")
        Sudoku.reset_counter()
        try:
            self.log("[worker]: 开始求解")
            s.solve_true_candidates()
        except InterruptedError:
            self.log("[worker]: 求解被中止")
        except Exception as e:
            self.log("[worker]: " + str(e))
        else:
            self.out_q.put(s.tuf_board.copy())
            self.log("[worker]: Solver finished.")
        finally:
            self.out_q.put(None)
        
    def log(self, message: str):
        """
        将日志信息追加到日志显示框中。
        为了线程安全，这里用 after 方法在主线程中更新 Text 控件
        """
        def append():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        self.root.after(0, append)

def run():
    ui = SudokuUI()

    ui.curr_puzzle_board = np.array([
        [9, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 1, 0, 0, 0, 3],
        [0, 1, 0, 0, 0, 0, 0, 6, 0],
        [0, 0, 0, 4, 0, 0, 0, 7, 0],
        [7, 0, 8, 6, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 3, 0, 1, 0, 0],
        [4, 0, 0, 0, 0, 0, 2, 0, 0]
    ])

    sum_pos_list = [(1,1), (1,2), (1,3), (1,4)]
    prod_pos_list = [(1,5)]
    oac = OrdArrowConstraint(sum_pos_list, prod_pos_list)
    ui.constraint = [oac]

    # ui.root.after(100, ui.start_solver)

    ui.root.mainloop()
    