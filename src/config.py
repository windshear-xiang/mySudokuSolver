'''
主程序会读取这里定义的 `CONFIG_PUZZLE_BOARD` 和 `CONFIG_CONSTRAINTS` 两个常量，并以此为基础启动app
'''

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
oac = OrdArrowConstraint(sum_pos_list, prod_pos_list, prep_at_init=False)

CONFIG_CONSTRAINTS = [oac]