"""模型层
"""

from typing import Sequence
import numpy as np
import json_tricks as json
from copy import deepcopy
from src.utils.type_definitions import *
from src.constraints import Constraint

class SudokuModel:
    def __init__(self,
                 puzzle_board: NumBoard,
                 constraints: list[Constraint],
                 log
                 ) -> None:

        # 当前显示的棋盘
        self.curr_puzzle_board = puzzle_board
        self.curr_tuf_board = np.zeros((9, 9, 9), dtype=np.int8)

        # Constraints
        self.constraints = constraints

        # controller传入的日志生成器
        self.log = log

        # 用于撤销和恢复的历史
        self.history = []
        self.history_pointer = 0 # 指示当前历史版本编号
        self._build_new_history()
    
    def get_constraint_cells(self, index) -> list:
        """返回第 index 个 constraint 的 cells 的副本"""
        if index >= len(self.constraints):
            self.log(f"访问的 constraint C{index} 不存在")
            return []
        return deepcopy([(i, j) for i,j in self.constraints[index].cells])

    def get_constraint_params(self, index) -> None | dict:
        """返回第 index 个 constraint 的 params 的副本"""
        if index >= len(self.constraints):
            self.log(f"访问的 constraint C{index} 不存在")
            return None
        return deepcopy(self.constraints[index].params)
    
    def add_constraint(self, ConstraintClass: type):
        """创建一个 ConstraintClass 类型的默认约束规则，加在列表最后"""
        try:
            if not issubclass(ConstraintClass, Constraint):
                raise TypeError(f"{ConstraintClass.__name__} 不是合法的 constraint 类型")
            new_constraint = ConstraintClass.create_default()
        except Exception as e:
            self.log(f"创建 {ConstraintClass.__name__} 失败: {str(e)}")
            return False
        else:
            self.constraints.append(new_constraint)
            self.log(f"创建 {ConstraintClass.__name__} 成功")
            self._build_new_history()
            return True

    def config_constraint(self, cells, params, index):
        """用参数 cells, params 重新生成 constraint 替换 index 位置的"""
        if index >= len(self.constraints):
            self.log(f"要修改的 constraint C{index} 不存在")
            return False
        ConstraintClass = self.constraints[index].__class__
        try:
            new_constraint = ConstraintClass(cells=cells, params=params, prep_at_init=False)
        except Exception as e:
            self.log(f"修改 constraint C{index} 失败: {str(e)}")
            return False
        else:
            self.constraints[index] = new_constraint
            self.log(f"修改 constraint C{index} 成功")
            self._build_new_history()
            return True

    def del_constraint(self, index):
        """返回是否真的删掉了"""
        if index >= len(self.constraints):
            self.log(f"要删除的 constraint C{index} 不存在")
            return False
        self.log(f"已删除 C{index} {self.constraints[index].info}")
        self.constraints.pop(index)
        self._build_new_history()
        return True

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
            "constraints": [
                {
                    "default_obj": constraint.__class__.create_default(), # 创建一个默认对象，用来记住这个类
                    "cells": constraint.cells,
                    "params": constraint.params
                }
                for constraint in self.constraints
            ]
        }
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(obj, file, indent=None)
        return
    
    def load_from_file(self, file_path):        
        with open(file_path, 'r', encoding='utf-8') as file:
            obj = json.load(file)
        self.curr_puzzle_board = obj["curr_puzzle_board"]
        self.curr_tuf_board = obj["curr_tuf_board"]
        self.constraints = [
            recover_dict["default_obj"].__class__(
                cells = recover_dict["cells"],
                params = recover_dict["params"],
                prep_at_init = False
            )
            for recover_dict in obj["constraints"]
        ]
        # 这是可以撤回的操作
        self._build_new_history()
        return

    def _build_new_history(self):
        self.log(f"记录新的历史版本 {self.history_pointer + 1}")
        del self.history[self.history_pointer : ]
        self.history.append((deepcopy(self.curr_puzzle_board), deepcopy(self.constraints))) #要构造新列表
        self.history_pointer += 1

    def to_prev_history(self):
        """返回是否真的有撤回"""
        if self.history_pointer <= 1:
            self.log("无法撤回，已经是最早版本")
            return False
        self.history_pointer -= 1
        self.curr_puzzle_board, self.constraints = self.history[self.history_pointer - 1]
        self.curr_tuf_board = np.zeros((9, 9, 9), dtype=np.int8)
        self.log(f"已撤回到上一版本 {self.history_pointer}/{len(self.history)}")
        return True
    
    def to_next_history(self):
        """返回是否真的有恢复"""
        if self.history_pointer == len(self.history):
            self.log("无法恢复，已经是最新版本")
            return False
        self.history_pointer += 1
        self.curr_puzzle_board, self.constraints = self.history[self.history_pointer - 1]
        self.curr_tuf_board = np.zeros((9, 9, 9), dtype=np.int8)
        self.log(f"已恢复到下一版本 {self.history_pointer}/{len(self.history)}")
        return True

    def clear_results(self):
        """把 curr_tuf_board 置为 -2 表示不要显示"""
        self.curr_tuf_board.fill(-2)
