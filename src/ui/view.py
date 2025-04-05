"""视图层
"""

import textwrap
import numpy as np
import tkinter as tk
from src.utils.ordinal import digit2ord
from src.ui.logger import Logger

DIGIT_TO_ORD_STR = {n: str(digit2ord(n)) for n in range(1, 10)}

BOARD_SIDE_LENGTH = 90
SIDE_PANEL_WIDTH = 45

class SudokuView:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Sudoku Solver")
        self.raw_logger = Logger(self._log_append)
        self.log = self.raw_logger("view")

        # 视图层状态属性
        self.display_as_ord_var = tk.BooleanVar(value=False) # 序数显示模式

         # 构建棋盘及其它控件
        self._build_board()
        self._build_side_panel()

        # 可对外提供接口，绑定事件处理程序
        self.event_callbacks = {}
    
    def _log_append(self, message: str):
        """
        将日志信息追加到日志显示框中。
        为了线程安全，这里用 after 方法在主线程中更新 Text 控件
        """
        def append():
            self.log_text.configure(state=tk.NORMAL) # 切换为可写入状态
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED) # 还原为不可写入状态
        self.root.after(0, append)

    def handle_event(self, event_type, *args):
        """视图层收集事件，再转发给 Controller 的事件处理函数"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type](*args)
        else:
            self.log(f"ERROR: event_type {event_type} cannot be handled.")

    def bind_event(self, event_type, callback):
        """供 Controller 注册各类事件处理函数"""
        self.event_callbacks[event_type] = callback
    
    def _build_board(self):
        """创建 9x9 网格，存放各格 Canvas"""
        self.cells: list[list[tk.Canvas]] = [[None for _ in range(9)] for _ in range(9)] # type: ignore
        for i in range(9):
            for j in range(9):
                canvas = tk.Canvas(self.root, width=90, height=90, 
                                     highlightthickness=0, bg='white')
                canvas.grid(row=i, column=j, padx=0, pady=0)
                # 绑定点击事件（仅在编辑状态下有效）
                canvas.bind("<Button-1>", lambda e, i=i, j=j: self.handle_event("cell_click", i, j))
                self.cells[i][j] = canvas
    
    def _build_side_panel(self):
        """创建右侧控制面板"""
        self.side_frame = tk.Frame(self.root)
        self.side_frame.grid(row=0, column=9, rowspan=9, padx=10, pady=10, sticky="n")

        # 在 side_frame 顶部创建一个控制区（control_frame）用于放置勾选框和按钮
        self.control_frame = tk.Frame(self.side_frame)
        self.control_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

        # 自动求解的勾选框【注意这个放在控制层了】
        self.auto_solve_cb = tk.Checkbutton(self.control_frame, text="Auto Solve")
        self.auto_solve_cb.grid(row=0, column=0, padx=5)

        # 序数显示的勾选框
        self.display_as_ord_cb = tk.Checkbutton(self.control_frame, text="Display as Ordinal", variable=self.display_as_ord_var)
        self.display_as_ord_cb.grid(row=0, column=1, padx=5)

        # 求解的按钮
        self.solve_button = tk.Button(self.control_frame, text="Solve True Candidates", command=lambda: self.handle_event("start_solver"))
        self.solve_button.grid(row=1, column=0, padx=5, pady=10)

        # 强行停止求解的按钮
        self.stop_button = tk.Button(self.control_frame, text="Force Stop", command=lambda: self.handle_event("stop_solver"))
        self.stop_button.grid(row=1, column=1, padx=5, pady=10)

        # 在控制区下方增加一行，用于 "Save" 和 "Load" 按钮
        self.sl_frame = tk.Frame(self.control_frame)
        self.sl_frame.grid(row=2, column=0, padx=5, pady=5)

        self.save_button = tk.Button(self.sl_frame, text="Save", command=lambda: self.handle_event("save"))
        self.save_button.grid(row=0, column=0, padx=5, pady=10)

        self.load_button = tk.Button(self.sl_frame, text="Load", command=lambda: self.handle_event("load"))
        self.load_button.grid(row=0, column=1, padx=5, pady=10)

        # 撤销和恢复
        self.unredo_frame = tk.Frame(self.control_frame)
        self.unredo_frame.grid(row=2, column=1, padx=5, pady=5)

        self.undo_button = tk.Button(self.unredo_frame, text="Undo", command=lambda: self.handle_event("undo"))
        self.undo_button.grid(row=0, column=0, padx=5, pady=10)

        self.redo_button = tk.Button(self.unredo_frame, text="Redo", command=lambda: self.handle_event("redo"))
        self.redo_button.grid(row=0, column=1, padx=5, pady=10)

        # 日志显示框（用于显示文字信息）
        self.log_label = tk.Label(self.side_frame, text="LOG")
        self.log_label.pack(side=tk.TOP, anchor='w', padx=5, pady=(20, 0))
        self.log_text = tk.Text(self.side_frame, width=SIDE_PANEL_WIDTH, height=18, state=tk.DISABLED)
        self.log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # constraints 显示框，放在日志显示框下面
        self.constraint_label_frame = tk.Frame(self.side_frame, width=SIDE_PANEL_WIDTH)
        self.constraint_label_frame.pack(side=tk.TOP, anchor='w', padx=5, pady=(20, 0))

        self.constraint_label = tk.Label(self.constraint_label_frame, text="Constraints")
        self.constraint_label.grid(row=0, column=0, padx=5, pady=5)

        self.new_constraint_button = tk.Button(self.constraint_label_frame, text="New", command=lambda: self.handle_event("new_constraint"))
        self.new_constraint_button.grid(row=0, column=1, padx=5, pady=5)

        self.constraint_container = tk.Frame(self.side_frame, width=SIDE_PANEL_WIDTH, height=18, borderwidth=1, relief="groove")
        self.constraint_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_display(self, curr_puzzle_board, curr_tuf_board, constraints, selected_cell):
        """绘制棋盘格子内容"""
        for i in range(9):
            for j in range(9):
                canvas = self.cells[i][j]
                canvas.delete('all')
                self._draw_cell_borders(canvas, i, j)
                if curr_puzzle_board[i, j] != 0:
                    self._draw_assigned_number(canvas, curr_puzzle_board[i, j])
                else:
                    cell_data = curr_tuf_board[i, j]
                    true_cand_count = np.sum(cell_data == 1)
                    false_cand_count = np.sum(cell_data == -1)
                    if true_cand_count == 1 and false_cand_count == 8:
                        # 已确定的格子：画大数字
                        num = int(np.argmax(cell_data) + 1)
                        self._draw_big_number(canvas, num)
                    else:
                        # 未确定：绘制候选信息
                        self._draw_small_grid(canvas, cell_data)
                if selected_cell == (i, j):
                    self._highlight_cell(canvas)

    def _draw_cell_borders(self, canvas: tk.Canvas, i: int, j: int):
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
    
    def _highlight_cell(self, canvas: tk.Canvas):
        # 绘制红色选中框
        canvas.create_rectangle(2, 2, 88, 88, outline="red", width=3)
    
    def _draw_assigned_number(self, canvas: tk.Canvas, number: int):
        if self.display_as_ord_var.get():
            canvas.create_text(45, 45, text=DIGIT_TO_ORD_STR[number], font=('Arial', 26), fill='black')
        else:
            canvas.create_text(45, 45, text=str(number), font=('Arial', 40), fill='black')
    
    def _draw_big_number(self, canvas: tk.Canvas, number: int):
        if self.display_as_ord_var.get():
            canvas.create_text(45, 45, text=DIGIT_TO_ORD_STR[number], font=('Arial', 26), fill='blue')
        else:
            canvas.create_text(45, 45, text=str(number), font=('Arial', 40), fill='blue')
        
    def _draw_small_grid(self, canvas: tk.Canvas, cell_data: np.ndarray):
        # 无解情况
        if np.all(cell_data == -1):
            canvas.create_text(45, 45, text='X', font=('Arial', 40), fill='red')
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
            if self.display_as_ord_var.get():
                if num == 8:
                    x += 5
                canvas.create_text(x+3, y+3, text=DIGIT_TO_ORD_STR[num], font=('Arial', 9), fill=color)
            else:
                canvas.create_text(x, y, text=str(num), font=('Arial', 12), fill=color)

    def refresh_constraints(self, constraints):
        # 先清空原有内容
        for old_widget in self.constraint_container.winfo_children():
            old_widget.destroy()

        if len(constraints) == 0:
            empty_label = tk.Label(self.constraint_container, text="None.")
            empty_label.pack(fill=tk.X, padx=2, pady=2)
        # 为每个约束创建一个子 Frame，其内包含约束描述和删除按钮
        for index, constraint in enumerate(constraints):
            info = constraint.info

            # 创建子 Frame（每行显示一条 constraint）
            row_frame = tk.Frame(self.constraint_container, borderwidth=1, relief="sunken")
            row_frame.pack(fill=tk.X, padx=2, pady=2)

            # Label 显示约束描述
            label = tk.Label(row_frame, width=38, wraplength=250 ,text=f"C{index}: "+info)
            label.grid(row=0, column=0, padx=2)

            # 删除按钮，点击后调用 handle_event 并传入对应约束的id
            delete_button = tk.Button(
                row_frame,
                text="Del",
                command=lambda index=index: self.handle_event("delete_constraint", index)
            )
            delete_button.grid(row=0, column=1, padx=5, pady=5)
        return

