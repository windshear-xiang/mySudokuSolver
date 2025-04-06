import numpy as np
import time
from numba import njit, prange
import tkinter as tk
from src.utils.ordinal import Ordinal, digit2ord
from src.utils.coord_calc import *
from src.config import BOARD_SIDE_LENGTH
from src.utils.tkinter_polygon import create_approx_circle
from . import DenseMultiCellConstraint

class OrdArrowConstraint(DenseMultiCellConstraint):
    def __init__(self, sum_pos_list: list, prod_pos_list: list, prep_at_init: bool = True):
        self.sum_len = len(sum_pos_list)
        super().__init__(sum_pos_list + prod_pos_list, prep_at_init=prep_at_init)

    @property
    def sum_pos_list(self):
        return self.cell_positions[0:self.sum_len]
    
    @property
    def prod_pos_list(self):
        return self.cell_positions[self.sum_len:]
    
    @property
    def info(self) -> str:
        sl = [f"({x},{y})" for x,y in self.sum_pos_list.tolist()]
        pl = [f"({x},{y})" for x,y in self.prod_pos_list.tolist()]
        return f"OrdArrowConstraint\n{' * '.join(pl)} = {' + '.join(sl)}"
    
    def is_valid(self, assigned_board):
        return _numba_is_valid(assigned_board, self.sum_pos_list, self.prod_pos_list)
    
    def preprocess(self) -> None:
        print("Preprocessing...")
        time_counter = time.perf_counter()

        combo_count = _numba_preprocess(
            self.valid_combinations,
            self.cell_nums,
            self.rows, self.cols,
            self.sum_pos_list, self.prod_pos_list
        )
        
        print(f"Preprocessed. combo_count={combo_count}. time={time.perf_counter() - time_counter:.6f}")
        return
    
    def draw(self, board_canvas: tk.Canvas, color:str="gray"):
        line_width = BOARD_SIDE_LENGTH * 0.25
        radius = BOARD_SIDE_LENGTH * 0.4
        side_len = BOARD_SIDE_LENGTH * 0.3

        prod_center_xys = [calc_center(i, j) for i, j in self.prod_pos_list]
        sum_center_xys = [calc_center(i, j) for i, j in self.sum_pos_list]
        # arrow
        board_canvas.create_line(prod_center_xys + sum_center_xys,
                                 width=line_width, fill=color, stipple="gray50",
                                 arrow="last", arrowshape=(line_width*2, line_width*2, line_width))
        # prod
        for center_x, center_y in prod_center_xys:
            create_approx_circle(board_canvas,
                                 center_x, center_y, radius,
                                 fill=color, outline=color, width=2, stipple="gray50")
        # sum
        for center_x, center_y in sum_center_xys:
            board_canvas.create_rectangle(center_x - side_len,
                                          center_y - side_len,
                                          center_x + side_len,
                                          center_y + side_len,
                                          fill=color, outline=color, stipple="gray25")
        return

@njit(nogil=True)
def _numba_is_valid(assigned_board, sum_pos_list, prod_pos_list):
    board_sum = Ordinal([0])
    board_prod = Ordinal([1])
    sum_range = len(sum_pos_list)
    for i in range(sum_range):
        x,y = sum_pos_list[i]
        if assigned_board[x][y] == 0:
            return True
        else:
            board_sum = board_sum + digit2ord(assigned_board[x][y])
    prod_range = len(prod_pos_list)
    for i in range(prod_range):
        x,y = prod_pos_list[i]
        if assigned_board[x][y] == 0:
            return True
        else:
            board_prod = board_prod * digit2ord(assigned_board[x][y])
    return board_sum == board_prod
    
@njit(nogil=True, parallel=True)
def _numba_preprocess(valid_combinations: np.ndarray, cell_nums, rows, cols, sum_pos_list, prod_pos_list):
    combo_count = 0
    total = 9 ** cell_nums
    powers = 9 ** np.arange(cell_nums-1, -1, -1)

    for index in prange(total):
        # 为了线程安全，只好单开
        temp_board = np.zeros((9, 9), dtype=np.int8)

        # 将线性索引转换为多维索引
        combo = (index // powers) % 9

        for i in range(cell_nums):
            temp_board[rows[i], cols[i]] = combo[i] + 1

        if _numba_is_valid(temp_board, sum_pos_list, prod_pos_list):
            valid_combinations.flat[index] = True
            combo_count += 1
    
    return combo_count
