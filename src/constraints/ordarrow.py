import numpy as np
import time
from numba import njit, prange
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
