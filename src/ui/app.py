import tkinter as tk
import numpy as np
from threading import Lock, Thread
import time
from src.solver import Sudoku
from src.constraints import KillerConstraint, OrdArrowConstraint
from src.utils.ordinal import Ordinal

displayer = str

class SudokuUI:
    def __init__(self, s: Sudoku):
        self.root = tk.Tk()
        self.root.title("Sudoku Solver")
        
        self.lock = Lock()
        self.s = s
        self.current_array = self.s.tuf_board.copy()
        self.dirty = True
        
        # 创建9x9网格
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                canvas = tk.Canvas(self.root, width=90, height=90, 
                                 highlightthickness=0, bg='white')
                canvas.grid(row=i, column=j, padx=0, pady=0)
                
                # 绘制单元格边框
                self._draw_cell_borders(canvas, i, j)
                
                self.cells[i][j] = canvas # type: ignore
        
        self.update_display()
        self.root.after(100, self.check_update)
    
    def _draw_cell_borders(self, canvas, i, j):
        canvas.delete('all')
        
        canvas.create_line(0, 0, 0, 90, width=1, fill='#cccccc')
        canvas.create_line(0, 0, 90, 0, width=1, fill='#cccccc')
        canvas.create_line(89, 0, 89, 90, width=1, fill='#cccccc')
        canvas.create_line(0, 89, 90, 89, width=1, fill='#cccccc')
        
        if j % 3 == 0:
            canvas.create_line(0, 0, 0, 90, width=2)
        if i % 3 == 0:
            canvas.create_line(0, 0, 90, 0, width=2)
        if j % 3 == 2:
            canvas.create_line(89, 0, 89, 90, width=2)
        if i % 3 == 2:
            canvas.create_line(0, 89, 90, 89, width=2)

    def update_array(self, new_array):
        with self.lock:
            self.current_array = new_array.copy()
            self.dirty = True
    
    def check_update(self):
        if self.dirty:
            self.update_display()
            self.dirty = False
        self.root.after(100, self.check_update)
    
    def update_display(self):
        for i in range(9):
            for j in range(9):
                cell_data = self.current_array[i, j]
                ones = np.sum(cell_data == 1)
                neg_ones = np.sum(cell_data == -1)
                
                if ones == 1 and neg_ones == 8:
                    num = np.argmax(cell_data) + 1
                    self._draw_big_number(i, j, num)
                else:
                    self._draw_small_grid(i, j, cell_data)
    
    def _draw_big_number(self, i, j, number):
        canvas = self.cells[i][j]
        canvas.delete('all')
        # 重新绘制边框
        self._draw_cell_borders(canvas, i, j)
        canvas.create_text(45, 45, text=displayer(number), 
                         font=('Arial', 40), fill='blue')
    
    def _draw_small_grid(self, i, j, cell_data):
        canvas = self.cells[i][j]
        canvas.delete('all')
        # 重新绘制边框
        self._draw_cell_borders(canvas, i, j)
        
        for num in range(1, 10):
            idx = num - 1
            state = cell_data[idx]
            
            row = (num-1) // 3
            col = (num-1) % 3
            x = col * 30 + 15
            y = row * 30 + 15
            
            if state == -1:
                color = 'white'
            elif state == 1:
                color = 'blue'
            else:
                color = '#cccccc'
            
            canvas.create_text(x, y, text=displayer(num), 
                             font=('Arial', 10), fill=color)

def data_updater(ui: SudokuUI):
    while True:
        # 等待0.1秒
        sleep_time = 0.1
        time.sleep(sleep_time)
        
        # 生成新的数据
        new_data = ui.s.tuf_board.copy()
        
        # 更新UI的数据
        ui.update_array(new_data)

def run():
    # puzzle1 = np.array([
    #     [3, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [8, 0, 0, 0, 2, 0, 0, 0, 5],
    #     [0, 0, 0, 0, 0, 6, 0, 4, 0],
    #     [0, 3, 8, 0, 0, 7, 0, 0, 0],
    #     [2, 0, 0, 0, 0, 0, 0, 0, 9],
    #     [0, 0, 0, 4, 0, 0, 0, 2, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [6, 0, 0, 0, 8, 0, 0, 0, 1],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0]
    # ])
    # s = Sudoku(puzzle1, [])

    # puzzle = np.array([
    # [9, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 0, 0, 0, 0, 0],
    # [0, 2, 0, 0, 1, 0, 0, 0, 3],
    # [0, 1, 0, 0, 0, 0, 0, 6, 0],
    # [0, 0, 0, 4, 0, 0, 0, 7, 0],
    # [7, 0, 8, 6, 0, 0, 0, 0, 0],
    # [0, 0, 0, 0, 3, 0, 1, 0, 0],
    # [4, 0, 0, 0, 0, 0, 2, 0, 0]
    # ])
    # sum_pos_list = [(1,1), (1,2), (1,3), (1,4)]
    # prod_pos_list = [(1,5)]
    # Sudoku.reset_counter()
    # s = Sudoku(puzzle, [OrdArrowConstraint(sum_pos_list, prod_pos_list)])
    # displayer = Ordinal.digit2ord

    # puzzle = np.array([
    #     [9, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 2, 0, 0, 1, 0, 0, 0, 3],
    #     [0, 1, 0, 0, 0, 0, 0, 6, 0],
    #     [0, 0, 0, 4, 0, 0, 0, 7, 0],
    #     [7, 0, 8, 6, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 3, 0, 1, 0, 0],
    #     [4, 0, 0, 0, 0, 0, 2, 0, 0]
    # ])
    # sum_pos_list = [(1,1), (1,2), (1,3)]
    # prod_pos_list = [(1,4), (2,5)]
    # Sudoku.reset_counter()
    # s = Sudoku(puzzle, [OrdArrowConstraint(sum_pos_list, prod_pos_list)])
    # displayer = Ordinal.digit2ord

    puzzle = np.array([
        [9, 4, 0, 0, 0, 0, 0, 0, 8],
        [0, 0, 0, 0, 0, 0, 5, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 1, 0, 0, 0, 3],
        [0, 1, 0, 0, 0, 0, 0, 6, 0],
        [0, 0, 0, 4, 0, 0, 0, 7, 0],
        [7, 0, 8, 6, 0, 0, 0, 0, 0],
        [2, 0, 0, 0, 3, 0, 0, 0, 1],
        [4, 0, 0, 0, 0, 0, 2, 0, 0]
    ])
    pos_list = [(1,1), (1,2), (1,3), (2,3), (2,4), (2,5)]
    killer_sum = 26
    Sudoku.reset_counter()
    s = Sudoku(puzzle, [KillerConstraint(pos_list, killer_sum), KillerConstraint([(1,8), (2,8)], 10)])

    print("time =", Sudoku.get_counter_stat()[1], '\n')

    ui = SudokuUI(s)

    # 创建数据更新线程
    updater_thread = Thread(target=data_updater, args=(ui,), daemon=True)
    # 创建求解线程
    solver_thread = Thread(target=s.solve_true_candidates)

    Sudoku.reset_counter()
    updater_thread.start()
    solver_thread.start()
    
    ui.root.mainloop()