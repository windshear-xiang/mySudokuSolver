import numpy as np
from src.constraints import OrdArrowConstraint

CONFIG_PUZZLE_BOARD = np.array([
    [9, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 1, 0, 0, 0, 3],
    [0, 1, 0, 0, 0, 0, 0, 6, 0],
    [0, 0, 0, 4, 0, 0, 0, 7, 0],
    [7, 0, 8, 6, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 3, 0, 1, 0, 0],
    [4, 0, 0, 0, 0, 0, 2, 0, 0]
])

sum_pos_list = [(1,1), (1,2), (1,3), (1,4)]
prod_pos_list = [(1,5)]
oac = OrdArrowConstraint(sum_pos_list, prod_pos_list)

CONFIG_CONSTRAINTS = [oac]