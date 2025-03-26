import numpy as np
from typing import Sequence
from src.constraints import Constraint
from src.utils.type_definitions import *

class SolvingBoard:
    '''
    This is an auxiliary class required when solving sudoku.

    Attributes:
        candidates_board: a 9x9x9 numpy ndarray, each indicate whether on a specific posisiton a specific number is available (`True` -> available; `False` -> unavailable). Note the index is `0-8`.
        assigned_board: a 9x9 numpy ndarray, each indicate the number assigned on the posisiton. `0` means not assigned.
    
    constraints 需要手工指定
    '''

    __slots__ = ("candidates_board", "assigned_board",)
    constraints: Sequence[Constraint] = []

    def __init__(self,
                 puzzle: NumBoard,
                 possible_cands: CandBoard
                 ) -> None:
        self.assigned_board: NumBoard = np.zeros((9,9), dtype=np.int8)
        self.candidates_board: CandBoard = possible_cands
        
        rows, cols = np.nonzero(puzzle)
        nums = puzzle[rows, cols]
        for (i, j), num in zip(zip(rows, cols), nums):
            succ = self.settle((i, j), num)
            if not succ:
                    raise Exception(f"Sudoku puzzle is incompatible at {i,j}.")
    
    def __str__(self) -> str:
        return self.assigned_board.__str__()
    
    def settle(self, pos: Position, num: int | np.int_) -> bool:
        '''
        Settle a specific number `num` on a specific position `pos`.

        This method will automatically eliminate the candidates in the row, column, and block where the num is settled. It will also eliminate some other candidates in accordance with the constraints.

        The `candidates_board` on the setteled position will be set as all zero.

        Args:
            pos: `tuple` of two `int`, with range `0-8`
            num: `int`, range `1-9`.
        '''

        assert num != 0
        x, y = pos

        if self.candidates_board[x,y,num-1] != True:
            return False

        # if already settled
        if self.assigned_board[x, y] == num:
            return True
        elif self.assigned_board[x, y] != 0:
            return False

        # Settle
        self.assigned_board[x, y] = num
        self.candidates_board[x, y, :] = False

        # Eliminate row & col candidates
        self.candidates_board[x, :, num-1] = False
        self.candidates_board[:, y, num-1] = False
        # Eliminate block candidates
        xb = (x // 3) * 3
        yb = (y // 3) * 3
        self.candidates_board[xb:xb+3, yb:yb+3, num-1] = False
        # Eliminate candidates in accordance with constraints
        for constraint in SolvingBoard.constraints:
            self.candidates_board &= constraint.available_candidates(self.assigned_board)

        # Check if there's enough candidates
        if np.any(np.all(self.candidates_board == False, axis=2) & (self.assigned_board == 0)):
            return False

        return True
    
    def get_least_cand_pos(self) -> tuple[int, Position | None]:
        '''
        Scan the whole candidates board,
        find the unassigned cell with the least candidates number.

        Return a `tuple` of `(the_least_candidates_count, the_cell_position)`

        Return `(0, None)` if there's no unassigned cell.
        '''
        assigned = self.assigned_board != 0
        if np.all(assigned):
            return 0, None
        cand_counts = np.sum(self.candidates_board, axis=2)
        cand_counts[assigned] = 10  # replace assigned position with 10, which is bigger than any other cell
        i, j = np.unravel_index(np.argmin(cand_counts), (9, 9))
        cand_count = cand_counts[i, j]
        return cand_count, (i, j)
        
    def quickdrops(self):

        checked = 0

        while True:
            # unique cand cells
            unique_positions = np.argwhere(np.sum(self.candidates_board, axis=2) == 1)
            checked += len(unique_positions) == 0
            for i, j in unique_positions:
                checked = 0
                num = self.candidates_board[i,j].argmax()
                succ = self.settle((i, j), num+1)
                if not succ:
                    return False
            
            if checked >= 3:
                break
                
            # uniqueness in row
            row_x_nums = np.argwhere(np.sum(self.candidates_board, axis=1) == 1)
            checked += len(row_x_nums) == 0
            for i, num in row_x_nums:
                checked = 0
                j = self.candidates_board[i, :, num].argmax()
                # Note that `num` ranges 0-8
                succ = self.settle((i, j), num+1)
                if not succ:
                    return False
            
            if checked >= 3:
                break
            
            # uniqueness in col
            col_x_nums = np.argwhere(np.sum(self.candidates_board, axis=0) == 1)
            checked += len(col_x_nums) == 0
            for j, num in col_x_nums:
                checked = 0
                i = self.candidates_board[:, j, num].argmax()
                # Note that `num` ranges 0-8
                succ = self.settle((i, j), num+1)
                if not succ:
                    return False
            
            if checked >= 3:
                break
            
        return True
    