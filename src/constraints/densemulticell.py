import numpy as np
import time
from functools import lru_cache
from itertools import product
from typing import Sequence
from src.utils.type_definitions import *
from . import Constraint

class DenseMultiCellConstraint(Constraint):
    '''
    This is a useful abstract base class for any constraint on multiple cells.

    Subclasses must implement `is_valid`.
    The method `available_candidates` will be implemented automatically.
    '''

    def __init__(self, ls: Sequence[Position], prep_at_init: bool = True) -> None:
        self.cell_positions = np.array(ls).astype(np.intp)
        self.cell_nums = len(ls)
        self.rows = self.cell_positions[:, 0]
        self.cols = self.cell_positions[:, 1]

        self.valid_combinations = np.zeros((9,) * self.cell_nums, dtype=np.bool_)

        self.preprocessed_flag = False

        if prep_at_init == True:
            self.preprocess()
            self.preprocessed_flag = True
        
    
    def preprocess(self) -> None:
        '''这个方法有可能被子类重写，不要在这里改 `self.precrocessed_flag` '''
        print("Preprocessing...")
        combo_count = 0
        time_counter = time.perf_counter()

        temp_board = np.zeros((9, 9), dtype=np.int8)
        for combo in product(range(1, 10), repeat=self.cell_nums):
            temp_board.fill(0)
            temp_board[self.rows, self.cols] = combo  # 向量化赋值
            if self.is_valid(temp_board):
                indices = tuple(num - 1 for num in combo)
                self.valid_combinations[indices] = True
                combo_count += 1
        
        print(f"Preprocessed. combo_count={combo_count}. time={time.perf_counter() - time_counter:.6f}")
        return
    
    def available_candidates(self, assigned_board: NumBoard) -> CandBoard:
        if not self.preprocessed_flag:
            self.preprocess()
            self.preprocessed_flag = True
        values = assigned_board[self.rows, self.cols]
        return self.valuetuple_to_candboard(tuple(values))

    @lru_cache(maxsize=4096)
    def valuetuple_to_candboard(self, values: tuple) -> CandBoard:
        cand_board = np.ones((9, 9, 9), dtype=np.bool_)
        slices = []
        unassigneds = []

        for num, x, y in zip(values, self.rows, self.cols):
            if num > 0:
                slices.append(num-1)
            else:
                slices.append(slice(None))
                unassigneds.append((num, x, y))
            
        subarray = self.valid_combinations[tuple(slices)]
        
        for idx, (num, x, y) in enumerate(unassigneds):
            possible_cands = np.moveaxis(subarray, idx, 0).reshape(9, -1).any(axis=1)
            cand_board[x, y] &= possible_cands
        
        return cand_board
