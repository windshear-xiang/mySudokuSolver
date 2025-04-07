import numpy as np
import time
from numba import njit, prange
from typing import Sequence
import tkinter as tk
from . import DenseMultiCellConstraint
from src.utils.coord_calc import *
from src.ui.ui_config import BOARD_SIDE_LENGTH
from src.utils.tkinter_polygon import create_cutted_rectangle
from src.utils.type_definitions import *

class KillerConstraint(DenseMultiCellConstraint):

    @staticmethod
    def create_constraint(cells, killer_sum, prep_at_init: bool = True):
        """用传统方法生成 Constraint 对象的工厂方法"""
        return KillerConstraint(
            cells,
            {"killer_sum": killer_sum},
            prep_at_init
        )

    def initialize(self, cells, params, prep_at_init: bool = True):
        self.killer_sum = params["killer_sum"]
        assert isinstance(self.killer_sum, int)
        return super().initialize(cells, params, prep_at_init)
    
    @property
    def info(self) -> str:
        sl = [f"({x},{y})" for x,y in self.cell_positions.tolist()]
        return f"{' + '.join(sl)} = {self.killer_sum}"
    
    def is_valid(self, assigned_board: NumBoard) -> bool:
        return _numba_is_valid(assigned_board, self.rows, self.cols, self.killer_sum)
    
    def preprocess(self) -> None:
        print("Preprocessing...")
        time_counter = time.perf_counter()

        combo_count = _numba_preprocess(
            self.valid_combinations,
            self.cell_nums,
            self.rows, self.cols,
            self.killer_sum
        )
        
        print(f"Preprocessed. combo_count={combo_count}. time={time.perf_counter() - time_counter:.6f}")
        return
    
    def draw(self, board_canvas: tk.Canvas, color:str="gray"):
        pad = 10
        text_size = 16
        min_x0 = float("inf")
        min_y0 = float("inf")
        tupled_cell_positions = [(x, y) for x, y in self.cell_positions]
        for (i, j) in tupled_cell_positions:
            x0, y0 = calc_left_top(i, j)
            x1, y1 = calc_right_bottom(i, j)
            # 找出最左边的格子里最靠上的，用来放sum数字
            if x0 <= min_x0:
                min_x0 = x0
                if y0 <= min_y0:
                    min_y0 = y0
            # 没有相邻的就往回缩
            cut_top, cut_bottom, cut_left, cut_right = False, False, False, False
            if (i, j+1) not in tupled_cell_positions:
                cut_right = True
            if (i, j-1) not in tupled_cell_positions:
                cut_left = True
            if (i+1, j) not in tupled_cell_positions:
                cut_bottom = True
            if (i-1, j) not in tupled_cell_positions:
                cut_top = True
            create_cutted_rectangle(board_canvas,
                                    x0, y0, x1, y1,
                                    cut_top=cut_top,
                                    cut_bottom=cut_bottom,
                                    cut_left=cut_left,
                                    cut_right=cut_right,
                                    pad=pad,
                                    fill=color, outline="", stipple="gray50")
        board_canvas.create_text(min_x0 + pad/2, min_y0 + pad/2, text=str(self.killer_sum),
                                 font=('Arial', text_size), fill="red")

@njit(nogil=True)
def _numba_is_valid(board: np.ndarray, rows: np.ndarray, cols: np.ndarray, killer_sum: int) -> bool:
    sum = 0
    for i in range(len(rows)):
        val = board[rows[i], cols[i]]
        if val == 0:
            # 发现未填数字，保持约束有效
            return True  
        sum += val
    return sum == killer_sum

@njit(nogil=True, parallel=True)
def _numba_preprocess(valid_combinations: np.ndarray, cell_nums, rows, cols, killer_sum):
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

        if _numba_is_valid(temp_board, rows, cols, killer_sum):
            valid_combinations.flat[index] = True
            combo_count += 1
    
    return combo_count