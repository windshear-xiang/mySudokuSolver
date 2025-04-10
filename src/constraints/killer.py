import numpy as np
import time
from numba import njit, prange
from typing import Sequence
import tkinter as tk
from . import DenseMultiCellConstraint
from src.utils.coord_calc import *
from src.ui_config import BOARD_SIDE_LENGTH
from src.utils.tkinter_polygon import create_cutted_rectangle
from src.utils.type_definitions import *
from src.utils.check_conflict import numba_has_conflict

class KillerConstraint(DenseMultiCellConstraint):

    @classmethod
    def create_constraint(cls, cells, killer_sum, prep_at_init: bool = True):
        """用传统方法生成 Constraint 对象的工厂方法，给老代码留个接口"""
        return cls(
            cells,
            {"killer_sum": killer_sum},
            prep_at_init
        )
    
    @classmethod
    def create_default(cls):
        return cls(
            cells = [(0, 0)],
            params = {"killer_sum": 0},
            prep_at_init = False
        )

    def initialize(self, cells, params, prep_at_init: bool = True):
        self.killer_sum = int(params["killer_sum"])
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
        tupled_cell_positions = [(i, j) for i, j in self.cell_positions]
        for (i, j) in tupled_cell_positions:
            x0, y0 = calc_left_top(i, j)
            x1, y1 = calc_right_bottom(i, j)
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
        # 找出最上边的格子里最靠左的，用来放sum数字
        min_i, min_j = min(tupled_cell_positions)
        min_x0, min_y0 = calc_left_top(min_i, min_j)
        board_canvas.create_text(min_x0 + text_size/2, min_y0 + text_size/2, text=str(self.killer_sum),
                                 font=('Arial', text_size), fill="red")

@njit(nogil=True)
def _numba_is_valid(board: np.ndarray, rows: np.ndarray, cols: np.ndarray, killer_sum: int) -> bool:
    if numba_has_conflict(board):
        return False
    sum = 0
    seen = np.zeros(10, dtype=np.bool_)
    for i in range(len(rows)):
        val = board[rows[i], cols[i]]
        if val == 0:
            # 发现未填数字，保持约束有效
            return True
        if seen[val]:
            return False
        seen[val] = True
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