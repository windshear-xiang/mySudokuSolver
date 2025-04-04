"""模型层
"""

from typing import Sequence
import numpy as np
import json_tricks as json
from src.utils.type_definitions import *
from src.constraints import Constraint

class SudokuModel:
    def __init__(self,
                 puzzle_board: NumBoard = np.zeros((9, 9), dtype=np.int8),
                 constraints: Sequence[Constraint] = []
                 ) -> None:

        # 当前显示的棋盘
        self.curr_puzzle_board = puzzle_board
        self.curr_tuf_board = np.zeros((9, 9, 9), dtype=np.int8)

        # Constraints
        self.constraints = constraints 
    
    def set_digit(self, i, j, digit):
        """返回是否真的有修改"""
        assert digit != 0
        if self.curr_puzzle_board[i, j] != digit:
            self.after_add()
            if self.curr_puzzle_board[i, j] != 0:
                self.after_del()
            self.curr_puzzle_board[i, j] = digit
            return True
        return False

    def del_digit(self, i, j):
        """返回是否真的有修改"""
        if self.curr_puzzle_board[i, j] != 0:
            self.after_del()
            self.curr_puzzle_board[i, j] = 0
            return True
        return False

    def after_add(self):
        '''加入新的数字/constraint 之后，之前正确的可能错，但是之前错的肯定还错'''
        self.curr_tuf_board[self.curr_tuf_board == 1] = 0
    
    def after_del(self):
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
        return
