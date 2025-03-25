import numpy as np
import time
from itertools import product
from numba import njit
from src.utils.ordinal import Ordinal, digit2ord
from . import DenseMultiCellConstraint

class OrdArrowConstraint(DenseMultiCellConstraint):
    def __init__(self, sum_pos_list: list, prod_pos_list: list):
        self.sum_len = len(sum_pos_list)
        super().__init__(sum_pos_list + prod_pos_list)

    @property
    def sum_pos_list(self):
        return self.cell_positions[0:self.sum_len]
    
    @property
    def prod_pos_list(self):
        return self.cell_positions[self.sum_len:]
    
    def is_valid(self, assigned_board):
        return _numba_is_valid(assigned_board, self.sum_pos_list, self.prod_pos_list)

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