"""这个模块提供了一个检查数独棋盘上哪些格子有冲突的工具
"""

from itertools import product
from .type_definitions import *
import numpy as np
from numba import njit

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

@njit(nogil=True, cache=True)
def numba_has_conflict(board: NumBoard):
    # 检查每一行
    for i in range(9):
        seen = np.zeros(10, dtype=np.bool_)  # 标记 0-9 是否出现过
        for j in range(9):
            num = board[i, j]
            if num == 0:
                continue
            if seen[num]:
                return True  # 行重复
            seen[num] = True

    # 检查每一列
    for j in range(9):
        seen = np.zeros(10, dtype=np.bool_)
        for i in range(9):
            num = board[i, j]
            if num == 0:
                continue
            if seen[num]:
                return True  # 列重复
            seen[num] = True

    # 检查每个3x3宫格
    for block_row in range(3):
        for block_col in range(3):
            seen = np.zeros(10, dtype=np.bool_)
            start_row = block_row * 3
            start_col = block_col * 3
            for i in range(start_row, start_row + 3):
                for j in range(start_col, start_col + 3):
                    num = board[i, j]
                    if num == 0:
                        continue
                    if seen[num]:
                        return True  # 宫重复
                    seen[num] = True

    return False  # 无冲突