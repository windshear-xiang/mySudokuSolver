import numpy as np
import time
import copy
import sys
import threading
import queue
from typing import Optional, Sequence

from src.utils.type_definitions import *
from src.constraints import Constraint
from .solvingboard import SolvingBoard

OUTPUT_TIME_INTERVAL = 0.1

class Sudoku:
    '''The class of a particular sudoku game.'''

    search_counter = 0
    time_counter = 0

    x_indices, y_indices = np.indices((9,9))

    @classmethod
    def reset_counter(cls) -> None:
        cls.search_counter = 0
        cls.time_counter = time.perf_counter()
    
    @classmethod
    def get_counter_stat(cls):
        '''Return a `tuple` of `(search_count, cost_time)`.'''
        cost_time = time.perf_counter() - cls.time_counter
        return cls.search_counter, cost_time

    def __init__(self,
                 puzzle: NumBoard,
                 constraints: Sequence[Constraint] = [],
                 out_q: Optional[queue.Queue] = None,
                 stop_event: Optional[threading.Event] = None
                 ) -> None:
        self.puzzle_board: NumBoard = puzzle
        self.constraints:Sequence[Constraint] = constraints
        self.tuf_board: TufBoard = np.zeros((9, 9, 9), dtype=np.int8) # 0->Unknown; 1->true; -1->false
        # 多线程使用的属性
        self.out_q = out_q
        self.stop_event = stop_event
        self.output_timer = time.perf_counter()

    def init_settle(self):
        rows, cols = np.nonzero(self.puzzle_board)
        nums = self.puzzle_board[rows, cols]
        for (i, j), num in zip(zip(rows, cols), nums):
            # Eliminate row & col candidates
            self.tuf_board[i, :, num-1] = -1
            self.tuf_board[:, j, num-1] = -1
            # Eliminate block candidates
            xb = (i // 3) * 3
            yb = (j // 3) * 3
            self.tuf_board[xb:xb+3, yb:yb+3, num-1] = -1
            # Eliminate this cell
            self.tuf_board[i, j, :] = -1 
            self.tuf_board[i, j, num-1] = 1
        return

    @property
    def tu_board(self):
        return self.tuf_board >= 0
    
    def solve_step(self, curr_sol: SolvingBoard) -> SolvingBoard | None:
        '''
        A recursive function. Solve the sudoku for one step and then call itself for the following steps.

        Return a `SolvingBoard` object if finally solved;
        
        Return `None` if it's unsolvable.
        '''

        # 多线程控制
        if time.perf_counter() - self.output_timer > OUTPUT_TIME_INTERVAL:
            if self.out_q is not None and self.stop_event is not None:
                # 到轮次了，输出
                self.out_q.put(self.tuf_board.copy())
                time.sleep(OUTPUT_TIME_INTERVAL / 10)
                self.output_timer = time.perf_counter()
                # 被中止了
                if self.stop_event.is_set():
                    raise InterruptedError

        Sudoku.search_counter += 1

        # If all cells are assigned
        curr_solving_pos = curr_sol.get_least_cand_pos()[1]
        if not curr_solving_pos:
            # Check constraints
            for constraint in self.constraints:
                if not constraint.is_valid(curr_sol.assigned_board):
                    return None
            return curr_sol
        
        # If not all cells are assigned, try settling
        i,j = curr_solving_pos
        curr_cand_list = np.flatnonzero(curr_sol.candidates_board[i,j]) + 1

        restore_assigned_board = curr_sol.assigned_board
        restore_cand_board = curr_sol.candidates_board

        for candidate in curr_cand_list:

            curr_sol.assigned_board = restore_assigned_board.copy()
            curr_sol.candidates_board = restore_cand_board.copy()
            next_sol = curr_sol

            if not next_sol.settle(curr_solving_pos, candidate):
                continue
            
            if not next_sol.quickdrops():
                continue

            # Jump into deeper recursion
            ret_sol = self.solve_step(next_sol)
            if ret_sol:
                return ret_sol
        
        return None
    
    def solve(self, reset_counter = True):
        '''
        Solve the sudoku.
        
        `self.puzzle_board` will remain untouched.

        Return a `SolvingBoard` object if the puzzle is solved.

        Return `None` is the puzzle is not solvable.
        '''
        SolvingBoard.constraints = self.constraints
        init_sol = SolvingBoard(puzzle=self.puzzle_board, possible_cands=self.tu_board)
        if reset_counter:
            self.reset_counter()
        return self.solve_step(init_sol)
    
    def get_least_unknown_cand_pos(self) -> tuple[int, Position | None]:
        '''
        Scan the whole `tuf_board`,
        find the cell with the least unknown candidates number and having unknown candidates (>0).

        Return a `tuple` of `(count, position)`

        Return `(0, None)` if there's no cell with unknown candidates.
        '''
        ucount_board = np.sum(self.tuf_board == 0, axis=2)
        known_board = np.logical_or(ucount_board == 0, self.puzzle_board != 0)
        if np.all(known_board):
            return 0, None

        ucount_board[known_board] = 10 # replace known position with 10, which is bigger than any other cell
        i, j = np.unravel_index(np.argmin(ucount_board), (9, 9))
        
        u_count = ucount_board[i, j]
        return u_count, (i, j)

    def solve_true_candidates(self):

        self.output_timer = time.perf_counter()

        self.init_settle()
        SolvingBoard.constraints = self.constraints
        init_sol = SolvingBoard(self.puzzle_board, possible_cands=self.tu_board)
        qsucc = init_sol.quickdrops()
        if not qsucc:
            raise Exception(f"Sudoku puzzle is incompatible.")

        u_count, pos = self.get_least_unknown_cand_pos()
        while u_count and pos:
            i,j = pos
            u_cand_ls = np.flatnonzero(self.tuf_board[i,j] == 0) # range 0-8
            for u_cand in u_cand_ls:
                self.flush_tuf_count()
                try_sol = copy.deepcopy(init_sol)
                try_sol.candidates_board &= self.tu_board
                succ = try_sol.settle(pos, u_cand+1)
                if succ:
                    qsucc = try_sol.quickdrops()
                    if qsucc:
                        ret_sol = self.solve_step(try_sol)
                        if ret_sol:
                            # candidate is good
                            self.tuf_board[Sudoku.x_indices, Sudoku.y_indices, ret_sol.assigned_board-1] = 1
                            continue
                # candidate is bad
                self.tuf_board[i,j,u_cand] = -1
            self.flush_tuf_count()
            u_count, pos = self.get_least_unknown_cand_pos()
        return
    
    def count_tuf_cands(self):
        t = np.sum(self.tuf_board == 1)
        u = np.sum(self.tuf_board == 0)
        f = np.sum(self.tuf_board == -1)
        return t, u, f
    
    def flush_tuf_count(self):
        t,u,f = self.count_tuf_cands()
        sys.stdout.write(f"\rUnknown={u} True={t} False={f} in {time.perf_counter()-Sudoku.time_counter:.4f}s   ")
        sys.stdout.flush()
        return

    def print_true_candidates(self):
        res = []
        for i in range(9):
            res.append([[n+1 for n in range(9) if self.tuf_board[i,j,n] == 1] for j in range(9)])
        return res

def has_conflict(board: NumBoard, pos: Position, num: int) -> bool:
    i, j = pos
    ret = np.all(board[i, :] != num)
    ret &= np.all(board[:, j] != num)
    xb = (i // 3) * 3
    yb = (j // 3) * 3
    ret &= np.all(board[xb:xb+3, yb:yb+3] != num)
    return not ret

