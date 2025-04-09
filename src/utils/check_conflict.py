"""这个模块提供了一个检查数独棋盘上哪些格子有冲突的工具
"""

from itertools import product
from .type_definitions import *
import numpy as np

def get_conflict_board(assigned_board: NumBoard):
    conflict_board = np.zeros((9,9), dtype=bool)
    for row in range(9):
        _, idx, counts = np.unique(assigned_board[row, :], return_inverse=True, return_counts=True)
        conflict_board[row, :] |= (counts[idx] > 1)
    for col in range(9):
        _, idx, counts = np.unique(assigned_board[:, col], return_inverse=True, return_counts=True)
        conflict_board[:, col] |= (counts[idx] > 1)
    for xb, yb in product([0, 3, 6], repeat=2):
        _, idx, counts = np.unique(assigned_board[xb:xb+3, yb:yb+3], return_inverse=True, return_counts=True)
        conflict_board[xb:xb+3, yb:yb+3] |= (counts[idx] > 1).reshape((3, 3))
    return conflict_board & (assigned_board != 0)

def has_conflict(assigned_board: NumBoard):
    return np.any(get_conflict_board(assigned_board))