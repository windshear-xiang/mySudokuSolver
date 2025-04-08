import numpy as np
import time
from functools import lru_cache
from itertools import product
from typing import Any, Sequence
from src.utils.type_definitions import *
from .base import BaseConstraint

class DenseMultiCellConstraint(BaseConstraint):
    '''This is a useful abstract base class for any constraint on multiple cells, `available_candidates()` will be implemented automatically

    Attributes:
        _cells (list[Position]): 所涉及的格子坐标
        _params (dict[str, Any]): 所涉及的其他参数
        valid_combinations (np.ndarray): 记录预处理的结果
        preprocessed_flag (bool): 记录是否预处理过

    Notes:
        用户请不要改动:
            + `__init__()` 方法：构造函数，接收 cells 和 params 为前两个参数\n
              **注意：对象必须要能够仅用 `cells` 和 `params` 的内容完整重构出来**
            + `cells` 属性：返回 constraint 所涉及的格子坐标
            + `params` 属性：返回 constraint 所涉及的其他参数
        用户必须自己在子类里实现：
            + `info` 属性：用来打印展示的内容信息
            + `param_names` 属性：初始化需要用到的其他参数的名称列表
            + `is_valid()` 方法：检查棋盘是否满足限制规则
            + `draw()` 方法：在棋盘上绘制出限制规则
        推荐用户实现，但不是必须:
            + `initialize()` 方法：用户自定义的初始化，`__init__()` 的参数会原样传进来\n
              **用户需要自己检查输入的参数有没有问题**\n
              **记得调用 `super.initialize()` !!!**
    '''

    def __init__(self, cells: list, params: dict[str, Any], prep_at_init: bool = True, *args, **kwargs):
        super().__init__(cells, params, prep_at_init=prep_at_init, *args, **kwargs)

    def initialize(self, cells, params, prep_at_init: bool = True, *args, **kwargs):
        """子类记得调用一下我！"""
        self.cell_positions = np.asarray(self.cells, dtype=np.intp)
        self.cell_nums = len(self.cell_positions)
        self.rows = self.cell_positions[:, 0]
        self.cols = self.cell_positions[:, 1]
        self.valid_combinations = np.zeros((9,) * self.cell_nums, dtype=np.bool_)
        self.preprocessed_flag = False

        if prep_at_init == True:
            self.preprocess()
            self.preprocessed_flag = True
        return
    
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
        return self._valuetuple_to_candboard(tuple(values))

    @lru_cache(maxsize=4096)
    def _valuetuple_to_candboard(self, values: tuple) -> CandBoard:
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
