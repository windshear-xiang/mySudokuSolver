import numpy as np
import time
import copy
import sys
import threading
from queue import Queue
from typing import Optional, Sequence
from src.utils.type_definitions import *
from src.constraints import Constraint
from .solvingboard import SolvingBoard


# 至少要间隔这么久才会输出中间结果
OUTPUT_TIME_INTERVAL = 0.2

X_INDICES, Y_INDICES = np.indices((9,9))


class Sudoku:
    """The class of a particular sudoku game.

    Attributes:
        puzzle_board (NumBoard): 谜面的数组
        tuf_board (TufBoard): 存放 True / Unknown / False candidates的数组。0->Unknown; 1->true; -1->false
        constraints (Sequence[Constraint]): 外加限制规则的列表
        out_q (Queue | None): 多线程通信用的管道，用来放中间输出结果
        stop_event (threading.Event | None): 多线程通信用的事件，用来指示强行需要停止求解
        output_timer: 多线程通信用的计时器，用来记录上次输出中间结果的时间
        search_timer: 搜索用的计时器，用来计算求解耗时
        search_counter: 搜索用的计数器，用来记录搜索步数
    """

    def __init__(self,
                 puzzle: NumBoard,
                 constraints: Sequence[Constraint] = [],
                 out_q: Optional[Queue] = None,
                 stop_event: Optional[threading.Event] = None
                 ) -> None:
        """生成一个 Sudoku 实例对象

        Args:
            puzzle (NumBoard): 谜面的数组
            constraints (Sequence[Constraint]): 外加限制规则的列表
            out_q (Queue | None): 多线程通信用的管道，用来放中间输出结果
            stop_event (threading.Event | None): 多线程通信用的事件，用来指示强行需要停止求解
        """
        self.puzzle_board: NumBoard = puzzle
        self.tuf_board: TufBoard = np.zeros((9, 9, 9), dtype=np.int8)
        self.constraints: Sequence[Constraint] = constraints
        # 多线程使用的属性
        self.out_q: Optional[Queue] = out_q
        self.stop_event: Optional[threading.Event] = stop_event
        self.output_timer: float = time.perf_counter()
        # 求解的计时器和计数器
        self.search_timer: float = time.perf_counter()
        self.search_counter: int = 0

    def init_settle(self):
        """根据 puzzle_board 的情况初始化一下 tuf_board。

        并不会整个清零 tuf_board。
        已经填了数的格子，把那个数设置是 1(t)，其他数都是 -1(f)。
        把同行同列同块这些格子里，相应的数都设置位 -1(f)。
        """
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
    
    def reset_counter(self) -> None:
        """重置求解计时器"""
        self.search_counter = 0
        self.search_timer = time.perf_counter()
    
    def get_counter_stat(self) -> tuple[int, float]:
        """读取求解计时器，单位是秒
        
        Returns:
            tuple: (搜索步数, 消耗时间)
        """

        cost_time = time.perf_counter() - self.search_timer
        return self.search_counter, cost_time
    
    def solve_step(self, curr_sol: SolvingBoard) -> SolvingBoard | None:
        '''
        A recursive function. Solve the sudoku for one step and then call itself for the following steps.

        Return a `SolvingBoard` object if finally solved;
        
        Return `None` if it's unsolvable.
        '''

        # 多线程控制是否需要中止求解
        if self.stop_event is not None:
            if self.stop_event.is_set():
                raise InterruptedError

        self.search_counter += 1

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
            if ret_sol is not None:
                return ret_sol
        
        return None
    
    def solve(self, reset_counter = True):
        """求出一个解。
        `self.puzzle_board` will remain untouched.

        Args:
            reset_counter (bool): 是否重置计时器

        Returns:
            (SolvingBoard | None): 求出的解，如果无解，返回None
        """
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

    def solve_true_candidates(self, reset_counter = True):
        """求解 true candidates

        注意这个程序依赖于当前 `self.tuf_board` 的情况，并不会清零。
        求解过程会直接修改 tuf_board

        Args:
            reset_counter (bool): 是否重置计时器
        """

        # 重置多线程输出计时器
        self.output_timer = time.perf_counter()
        # 默认重置求解计时器
        if reset_counter:
            self.reset_counter()

        # 根据 puzzle_board 的情况初始化一下 tuf_board
        self.init_settle()
        # 创建用于求解的对象
        SolvingBoard.constraints = self.constraints
        init_sol = SolvingBoard(self.puzzle_board, possible_cands=self.tu_board)

        # 先预先 quickdrop 一次
        qsucc = init_sol.quickdrops()
        if not qsucc:
            #说明根本就无解
            raise Exception(f"Sudoku puzzle has no solution.")
        self.tuf_board[X_INDICES, Y_INDICES, init_sol.assigned_board-1] = 1

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
                        if ret_sol is not None:
                            # candidate is good
                            self.tuf_board[X_INDICES, Y_INDICES, ret_sol.assigned_board-1] = 1
                            continue
                # candidate is bad
                self.tuf_board[i,j,u_cand] = -1
            self.flush_tuf_count()
            u_count, pos = self.get_least_unknown_cand_pos()

            # 多线程控制 输出中间结果
            if time.perf_counter() - self.output_timer > OUTPUT_TIME_INTERVAL:
                if self.out_q is not None:
                    # 到轮次了，输出
                    self.out_q.put(self.tuf_board.copy())
                    # 让出GIL控制权给UI线程，避免卡死
                    time.sleep(OUTPUT_TIME_INTERVAL / 20)
                    self.output_timer = time.perf_counter()
                
        return
    
    def count_tuf_cands(self):
        """输出当前整个棋盘上 true, unknown, false 三种 candidate 的数目

        Returns:
            tuple: (t, u, f)
        """

        t = np.sum(self.tuf_board == 1)
        u = np.sum(self.tuf_board == 0)
        f = np.sum(self.tuf_board == -1)
        return t, u, f
    
    def flush_tuf_count(self):
        """在 sys.stdout 输出整个棋盘上true, unknown, false 三种 candidate 的数目，以及当前的总搜索步数和耗时"""
        t,u,f = self.count_tuf_cands()
        steps, times = self.get_counter_stat()
        sys.stdout.write(f"\rUnknown={u} True={t} False={f}, in {steps}steps {times:.4f}s   ")
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

