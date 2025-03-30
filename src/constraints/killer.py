import numpy as np
import time
from numba import njit, prange
from typing import Sequence
from . import DenseMultiCellConstraint
from src.utils.type_definitions import *

class KillerConstraint(DenseMultiCellConstraint):
    def __init__(self, ls: Sequence[Position], killer_sum: int) -> None:
        self.killer_sum = killer_sum
        super().__init__(ls)
    
    @property
    def info(self) -> str:
        sl = [f"({x},{y})" for x,y in self.cell_positions.tolist()]
        return f"KillerConstraint\n{' + '.join(sl)} = {self.killer_sum}\n"
    
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