import tkinter as tk
import numpy as np
from threading import Thread
from src.solver import Sudoku

class SudokuUI:
    def __init__(self, s: Sudoku):
        self.root = tk.Tk()
        self.root.title("Sudoku Solver")

        # 状态属性
        self.editable = True    # 编辑状态（允许输入/删除数字）
        self.selected_cell = None  # 当前选中的格子 (i, j)

        # 储存的数独类
        self.s = s
        # 当前显示的棋盘
        self.current_tuf_board = self.s.tuf_board.copy()
        self.current_puzzle_board = self.s.puzzle_board.copy()
        
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
        
        # Solve 按钮（点击启动求解）
        self.solve_button = tk.Button(self.side_frame, text="True Candidates", command=self.start_solver)
        self.solve_button.pack(side=tk.TOP, padx=5, pady=5)

        # 日志显示框（用于显示文字信息）
        self.log_text = tk.Text(self.side_frame, width=35, height=30, state=tk.NORMAL)
        self.log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 绑定键盘事件（全局绑定，编辑状态下处理数字和删除操作）
        self.root.bind("<Key>", self.on_key_pressed)
        
        # 定时刷新界面（每0.1秒检查一次更新）
        self.root.after(100, self.check_update)
    
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
        # 当处于编辑状态并且未开始求解时，用户点击格子选中该格子
        if not self.editable:
            return
        self.selected_cell = (i, j)
    
    def on_key_pressed(self, event):
        # 仅在编辑状态下响应键盘输入
        if not self.editable:
            return
        if self.selected_cell is None:
            return
        
        i, j = self.selected_cell
        # 如果按下数字键1~9，则设定该格的值，并标记为用户输入
        if len(event.char) == 1 and event.char.isdigit() and event.char != '0':
            digit = int(event.char)
            self.s.puzzle_board[i, j] = digit
            self.s.after_add()
        elif event.keysym in ("BackSpace", "Delete"):
            # 清空当前格（置为全0状态），并取消用户给定标记
            self.s.puzzle_board[i, j] = 0
            self.s.after_del()

    def check_update(self):
        # 每隔0.1秒刷新一次界面显示
        self.current_tuf_board = self.s.tuf_board.copy()
        self.current_puzzle_board = self.s.puzzle_board.copy()
        self.update_display()
        self.root.after(100, self.check_update)
    
    def update_display(self):
        for i in range(9):
            for j in range(9):
                # 重新绘制边框
                canvas = self.cells[i][j]
                canvas.delete('all')
                self._draw_cell_borders(canvas, i, j)

                if self.current_puzzle_board[i, j] != 0:
                    self._draw_assigned_number(canvas, self.current_puzzle_board[i, j])
                else:
                    cell_data = self.current_tuf_board[i, j]
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
            self.log("无解")
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
    
    def start_solver(self):
        # 用户点击“Solve”后，切换状态：禁止编辑和键盘输入，并禁用按钮
        if not self.editable:
            self.log("正在求解，请稍等")
            return
        self.editable = False
        self.selected_cell = None
        # 启动求解线程
        solver_thread = Thread(target=self.run_solver, daemon=True)
        solver_thread.start()
    
    def run_solver(self):
        # 调用 Sudoku 类中的 true_candidates 求解方法
        self.log("Solving...")
        Sudoku.reset_counter()
        try:
            self.s.solve_true_candidates()
        except Exception as e:
            self.log(str(e))
        else:
            self.log("Solver finished.")
        self.editable = True
    
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
    # 创建一个空棋盘，每个格子存储一个长度为9的候选状态数组（初始全为0）
    puzzle = np.zeros((9, 9), dtype=np.int8)

    # puzzle = np.array([
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 3, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 4, 0, 0, 5, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 5, 0, 0, 6, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 5, 0],
    #     [0, 8, 0, 0, 0, 0, 0, 4, 0],
    #     [0, 0, 0, 0, 0, 1, 0, 0, 0]
    # ])

    # 构造 Sudoku 对象，第二个参数为其他约束（此处置空）
    s = Sudoku(puzzle, [])
    ui = SudokuUI(s)
    ui.root.mainloop()

if __name__ == "__main__":
    run()