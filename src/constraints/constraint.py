'''
This module provide the abstract base class `Constraint` and  for constraints applied on Sudoku
'''

from abc import ABC, abstractmethod
import numpy as np
from src.utils.type_definitions import *

class Constraint(ABC):
    '''
    Base class for constraints applied on Sudoku.

    Subclasses must implement `is_valid`.
    '''
    
    @abstractmethod
    def is_valid(self, assigned_board: NumBoard) -> bool:
        '''
        Check if the board satisfies the constraint.

        Return `True` if uncertain (e.g. unassigned cells exist).

        User must implement this method themselves.
        '''
        pass
    
    def available_candidates(self, assigned_board: NumBoard) -> CandBoard:
        '''
        Return candidates after being eliminated based on the constraint.

        This method is the method actually used in the solving procedure.
        Default implementation returns all candidates as valid if constraint is satisfied.

        It's highly recommended, but not obligatory, for users to implement this method themselves.
        '''
        if self.is_valid(assigned_board):
            return np.ones((9, 9, 9), dtype=bool)
        else:
            return np.zeros((9, 9, 9), dtype=bool)
