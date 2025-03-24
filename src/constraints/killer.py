import numpy as np
from numba import njit
from typing import Sequence
from . import DenseMultiCellConstraint
from src.utils.type_definitions import *

class KillerConstraint(DenseMultiCellConstraint):
    def __init__(self, ls: Sequence[Position], killer_sum: int) -> None:
        self.killer_sum = killer_sum
        super().__init__(ls)
    
    @staticmethod
    @njit(nogil=True)
    def _is_valid_numba(board: np.ndarray, rows: np.ndarray, cols: np.ndarray, killer_sum: int) -> bool:
        sum = 0
        for i in range(len(rows)):
            val = board[rows[i], cols[i]]
            if val == 0:
                # 发现未填数字，保持约束有效
                return True  
            sum += val
        return sum == killer_sum
    
    def is_valid(self, assigned_board: NumBoard) -> bool:
        return KillerConstraint._is_valid_numba(assigned_board, self.rows, self.cols, self.killer_sum)
        # values = assigned_board[self.rows, self.cols]
        # if np.any(values == 0):
        #     return True
        # return np.sum(values) == self.killer_sum