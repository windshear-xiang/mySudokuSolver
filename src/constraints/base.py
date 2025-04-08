"""This module provide the abstract base class `BaseConstraint` for all constraints applied on Sudoku
"""

from abc import ABC, abstractmethod
from typing import Any
import numpy as np
from src.utils.type_definitions import *

class BaseConstraint(ABC):
    """Abstract Base class for all constraints applied on Sudoku.

    Attributes:
        _cells (list[Position]): 所涉及的格子坐标
        _params (dict[str, Any]): 所涉及的其他参数

    Notes:
        用户请不要改动:
            + `__init__()` 方法：构造函数，接收 cells 和 params 为前两个参数\n
              **注意：对象必须要能够仅用 `cells` 和 `params` 的内容完整重构出来**
            + `cells` 属性：返回 constraint 所涉及的格子坐标
            + `params` 属性：返回 constraint 所涉及的其他参数
        用户必须自己在子类里实现：
            + `initialize()` 方法：用户自定义的初始化，`__init__()` 的参数会原样传进来
            + `info` 属性：用来打印展示的内容信息
            + `is_valid()` 方法：检查棋盘是否满足限制规则
            + `draw()` 方法：在棋盘上绘制出限制规则
        推荐用户实现，但不是必须:
            + `available_candidates()` 方法
    """

    def __init__(self, cells: list, params: dict[str, Any], *args, **kwargs) -> None:
        """请不要改动这个方法
        
        必须传入 `cells: list[Position]` 和 `params :dict[str, Any]` 作为前两个参数

        对象必须要能够仅用 `cells` 和 `params` 的内容完整重构出来
        """
        self._cells = cells
        self._params = params
        self.initialize(cells, params, *args, **kwargs)
    
    @abstractmethod
    def initialize(self, cells: list, params: dict[str, Any], *args, **kwargs) -> None:
        """用户必须自己实现这个方法

        用户自定义的初始化，`__init__()` 的参数会原样传进来
        """
        pass

    @property
    @abstractmethod
    def info(self) -> str:
        """返回用来打印展示的 constraint 的内容信息，用户必须自己实现"""
        pass

    @property
    def cells(self) -> list:
        """返回 constraint 所涉及的格子坐标，请不要改动这个属性"""
        return self._cells

    @property
    def params(self) -> dict[str, Any]:
        """返回 constraint 所涉及的其他参数，请不要改动这个属性"""
        return self._params
    
    @abstractmethod
    def is_valid(self, assigned_board: NumBoard) -> bool:
        '''Check if the board satisfies the constraint.

        Return `True` if uncertain (e.g. unassigned cells exist).

        User must implement this method themselves.
        '''
        pass
    
    def available_candidates(self, assigned_board: NumBoard) -> CandBoard:
        '''Return candidates after being eliminated based on the constraint.

        This method is the method actually used in the solving procedure.
        Default implementation returns all candidates as valid if constraint is satisfied.

        It's highly recommended, but not obligatory, for users to implement this method themselves.
        '''
        if self.is_valid(assigned_board):
            return np.ones((9, 9, 9), dtype=bool)
        else:
            return np.zeros((9, 9, 9), dtype=bool)
    
    @abstractmethod
    def draw(self, canvas):
        """在棋盘上绘制出限制规则，用户必须自己实现"""
        pass
