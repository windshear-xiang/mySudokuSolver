import numpy as np
import pytest
from src.solver import Sudoku
from src.constraints import KillerConstraint
from src.utils.type_definitions import *

def test_cand_1():
    puzzle = np.array([
        [9, 4, 0, 0, 0, 0, 0, 0, 8],
        [0, 0, 0, 0, 0, 0, 5, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 2, 0, 0, 1, 0, 0, 0, 3],
        [0, 1, 0, 0, 0, 0, 0, 6, 0],
        [0, 0, 0, 4, 0, 0, 0, 7, 0],
        [7, 0, 8, 6, 0, 0, 0, 0, 0],
        [2, 0, 0, 0, 3, 0, 0, 0, 1],
        [4, 0, 0, 0, 0, 0, 2, 0, 0]
    ])

    cands = [
        [[9], [4], [2, 5, 6], [1, 2, 3, 5], [5, 6, 7], [2, 3, 5, 6, 7], [3, 7], [1, 2], [8]],
        [[1, 3, 6, 8], [7, 8], [2, 3, 6], [1, 3, 8], [6, 7, 8, 9], [6, 7, 8, 9], [5], [1, 2, 9], [4]],
        [[1, 3, 5, 8], [5, 7, 8], [2, 3, 5], [1, 2, 3, 5, 8, 9], [4], [2, 3, 5, 8, 9], [3, 7], [2, 9], [6]],
        [[5, 6, 8], [2], [4, 7], [5, 8, 9], [1], [5, 6, 7, 8, 9], [4, 8, 9], [4, 5], [3]],
        [[3, 5, 8], [1], [4, 7], [2, 3, 5, 8, 9], [5, 7, 8, 9], [2, 3, 5, 7, 8, 9], [4, 8, 9], [6], [2, 5, 9]],
        [[3, 5, 6, 8], [5, 8, 9], [3, 5, 6, 9], [4], [5, 6, 8], [2, 3, 5, 6, 8], [1], [7], [2, 5]],
        [[7], [3], [8], [6], [2], [1], [4, 9], [4, 5], [5, 9]],
        [[2], [5, 9], [5, 9], [7], [3], [4], [6], [8], [1]],
        [[4], [6], [1], [5, 8, 9], [5, 8, 9], [5, 8, 9], [2], [3], [7]]
    ]

    pos_list_1 = [(1,1), (1,2), (1,3), (2,3), (2,4), (2,5)]
    killer_sum_1 = 26
    kc1 = KillerConstraint(pos_list_1, killer_sum_1)

    pos_list_2 = [(1,8), (2,8)]
    killer_sum_2 = 10
    kc2 = KillerConstraint(pos_list_2, killer_sum_2)

    Sudoku.reset_counter()
    s = Sudoku(puzzle, [kc1, kc2])
    Sudoku.reset_counter()
    s.solve_true_candidates()
    print(Sudoku.get_counter_stat())
    assert s.print_true_candidates() == cands