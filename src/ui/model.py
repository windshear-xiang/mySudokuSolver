"""模型层
"""

from typing import Sequence
import numpy as np
import json_tricks as json
from src.utils.type_definitions import *
from src.constraints import Constraint

class SudokuModel:
    def __init__(self,
                 puzzle_board: NumBoard,
                 constraints: Sequence[Constraint],
                 log
                 ) -> None:

        # 当前显示的棋盘
        self.curr_puzzle_board = puzzle_board
        self.curr_tuf_board = np.zeros((9, 9, 9), dtype=np.int8)

        # Constraints
        self.constraints = constraints

        # 外界传入日志生成器
        self.log = log

        # 用于撤销和恢复的历史
        self.history = []
        self.history_pointer = 0 # 指示当前历史版本 + 1
        self._build_new_history()
    
    def set_digit(self, i, j, digit):
        """返回是否真的有修改"""
        assert digit != 0
        if self.curr_puzzle_board[i, j] != digit:
            self._after_add()
            if self.curr_puzzle_board[i, j] != 0:
                self._after_del()
            self.curr_puzzle_board[i, j] = digit
            # 这是可以撤回的操作
            self._build_new_history()
            return True
        return False

    def del_digit(self, i, j):
        """返回是否真的有修改"""
        if self.curr_puzzle_board[i, j] != 0:
            self.curr_puzzle_board[i, j] = 0
            self._after_del()
            # 这是可以撤回的操作
            self._build_new_history()
            return True
        return False

    def _after_add(self):
        '''加入新的数字/constraint 之后，之前正确的可能错，但是之前错的肯定还错'''
        self.curr_tuf_board[self.curr_tuf_board == 1] = 0
    
    def _after_del(self):
        '''删除已有的数字/constraint 之后，之前正确的还正确，但是之前错的可能对'''
        self.curr_tuf_board[self.curr_tuf_board == -1] = 0
    
    def save_to_file(self, file_path):
        obj = {
            "curr_puzzle_board": self.curr_puzzle_board,
            "curr_tuf_board": self.curr_tuf_board,
            "constraints": self.constraints
        }
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(obj, file, indent=None)
        return
    
    def load_from_file(self, file_path):        
        with open(file_path, 'r', encoding='utf-8') as file:
            obj = json.load(file)
        self.curr_puzzle_board = obj["curr_puzzle_board"]
        self.curr_tuf_board = obj["curr_tuf_board"]
        self.constraints = obj["constraints"]
        # 这是可以撤回的操作
        self._build_new_history()
        return

    def _build_new_history(self):
        self.log("记录新的历史版本")
        del self.history[self.history_pointer : ]
        self.history.append((self.curr_puzzle_board.copy(), [c for c in self.constraints]))
        self.history_pointer += 1

    def to_prev_history(self):
        if self.history_pointer <= 1:
            self.log("无法撤回，已经是最早版本")
            return
        self.history_pointer -= 1
        self.curr_puzzle_board, self.constraints = self.history[self.history_pointer - 1]
        self.curr_tuf_board = np.zeros((9, 9, 9), dtype=np.int8)
        self.log("已撤回到上一版本")
    
    def to_next_history(self):
        if self.history_pointer == len(self.history):
            self.log("无法恢复，已经是最新版本")
            return
        self.history_pointer += 1
        self.curr_puzzle_board, self.constraints = self.history[self.history_pointer - 1]
        self.curr_tuf_board = np.zeros((9, 9, 9), dtype=np.int8)
        self.log("已恢复到下一版本")

