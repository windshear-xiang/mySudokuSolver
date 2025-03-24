import numpy as np
from functools import lru_cache
from itertools import product
from src.utils.type_definitions import *
from . import Constraint

class DenseMultiCellConstraint(Constraint):
    '''
    This is a useful abstract base class for any constraint on multiple cells.

    Subclasses must implement `is_valid`.
    The method `available_candidates` will be implemented automatically.
    '''

    def __init__(self, ls: list[Position]) -> None:
        self.cell_positions = np.array(ls).astype(np.intp)
        self.cell_nums = len(ls)
        self.rows = self.cell_positions[:, 0]
        self.cols = self.cell_positions[:, 1]

        self.valid_combinations = np.zeros((9,) * self.cell_nums, dtype=np.bool_)
        self.preprocess()
    
    def preprocess(self) -> None:
        print("Preprocessing...")
        combo_count = 0

        temp_board = np.zeros((9, 9), dtype=np.int8)
        for combo in product(range(1, 10), repeat=self.cell_nums):
            temp_board.fill(0)
            temp_board[self.rows, self.cols] = combo  # 向量化赋值
            if self.is_valid(temp_board):
                indices = tuple(num - 1 for num in combo)
                self.valid_combinations[indices] = True
                combo_count += 1
        
        print(f"Preprocessed. combo_count={combo_count}")
        return
    
    def available_candidates(self, assigned_board: NumBoard) -> CandBoard:
        # return super().available_candidates(assigned_board)
        values = assigned_board[self.rows, self.cols]
        # if np.all(values > 0):
        #     return super().available_candidates(assigned_board)
        return self.valuetuple_to_candboard(tuple(values))

    @lru_cache(maxsize=None)
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
