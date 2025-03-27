import numpy as np
from typing import Sequence
from numba import njit
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
        '''注意__init__很慢，没有优化过，尽量少用'''
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

        succ = _numba_settle(self.candidates_board, self.assigned_board, x, y, num)
        if not succ:
            return False

        # Eliminate candidates in accordance with constraints
        for constraint in SolvingBoard.constraints:
            self.candidates_board &= constraint.available_candidates(self.assigned_board)

        # Check if there's enough candidates
        return _numba_check_after_settle(self.candidates_board, self.assigned_board)
    
    def get_least_cand_pos(self) -> tuple[int, Position | None]:
        '''
        Scan the whole candidates board,
        find the unassigned cell with the least candidates number.

        Return a `tuple` of `(the_least_candidates_count, the_cell_position)`

        Return `(0, None)` if there's no unassigned cell.
        '''
        cand_count, (i, j) = _numba_get_least_cand_pos(self.candidates_board, self.assigned_board)
        if cand_count == 10:
            return 0, None
        return cand_count, (i, j)
        
    def quickdrops(self):

        checked = 0

        while True:
            # unique cand cells
            i, j, num =_numba_find_unique_position(self.candidates_board)
            checked += 1
            if num >= 0:
                checked = 0
                succ = self.settle((i, j), num+1)
                if not succ:
                    return False
            if checked >= 3:
                break
                
            # uniqueness in row
            i, j, num =_numba_find_uniqueness_in_row(self.candidates_board)
            checked += 1
            if num >= 0:
                checked = 0
                succ = self.settle((i, j), num+1)
                if not succ:
                    return False
            if checked >= 3:
                break
            
            # uniqueness in col
            i, j, num =_numba_find_uniqueness_in_col(self.candidates_board)
            checked += 1
            if num >= 0:
                checked = 0
                succ = self.settle((i, j), num+1)
                if not succ:
                    return False
            if checked >= 3:
                break
            
        return True

@njit
def _numba_get_least_cand_pos(candidates_board, assigned_board):
    minv = 10
    mini = 0
    minj = 0
    for i in range(9):
        for j in range(9):
            if assigned_board[i, j] != 0:
                continue
            curr_sum = 0
            for cand in range(9):
                curr_sum += candidates_board[i, j, cand]
                if curr_sum >= minv:
                    break
            if curr_sum < minv:
                minv = curr_sum
                mini = i
                minj = j
    return minv, (mini, minj)


@njit
def _numba_settle(candidates_board, assigned_board, x, y, num):
    
    if candidates_board[x,y,num-1] != True:
        return False

    # if already settled
    if assigned_board[x, y] == num:
        return True
    elif assigned_board[x, y] != 0:
        return False

    # Settle
    assigned_board[x, y] = num
    candidates_board[x, y, :] = False

    # Eliminate row & col candidates
    candidates_board[x, :, num-1] = False
    candidates_board[:, y, num-1] = False
    # Eliminate block candidates
    xb = (x // 3) * 3
    yb = (y // 3) * 3
    candidates_board[xb:xb+3, yb:yb+3, num-1] = False

    return True

@njit
def _numba_check_after_settle(candidates_board, assigned_board):
    for i in range(9):
        for j in range(9):
            if assigned_board[i, j] != 0:
                continue
            no_cand_flag = True
            for num in range(9):
                if candidates_board[i, j, num] == True:
                    no_cand_flag = False
                    continue
            if no_cand_flag:
                return False
    return True

@njit
def _numba_find_unique_position(candidates_board):
    unqi = -1
    unqj = -1
    unqcand = -1
    for i in range(9):
        for j in range(9):
            curr_sum = 0
            for cand in range(9):
                if candidates_board[i, j, cand]:
                    curr_sum += 1
                    unqcand = cand
                    if curr_sum > 1:
                        break
            if curr_sum == 1:
                unqi = i
                unqj = j
                return unqi, unqj, unqcand
    return -1, -1, -1

@njit
def _numba_find_uniqueness_in_row(candidates_board):
    unqi = -1
    unqj = -1
    unqcand = -1
    for i in range(9):
        for cand in range(9):
            curr_sum = 0
            for j in range(9):
                if candidates_board[i, j, cand]:
                    curr_sum += 1
                    unqj = j
                    if curr_sum > 1:
                        break
            if curr_sum == 1:
                unqi = i
                unqcand = cand
                return unqi, unqj, unqcand
    return -1, -1, -1

@njit
def _numba_find_uniqueness_in_col(candidates_board):
    unqi = -1
    unqj = -1
    unqcand = -1
    for j in range(9):
        for cand in range(9):
            curr_sum = 0
            for i in range(9):
                if candidates_board[i, j, cand]:
                    curr_sum += 1
                    unqi = i
                    if curr_sum > 1:
                        break
            if curr_sum == 1:
                unqj = j
                unqcand = cand
                return unqi, unqj, unqcand
    return -1, -1, -1
    