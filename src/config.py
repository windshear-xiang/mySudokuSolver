'''
主程序会读取这里定义的 `CONFIG_PUZZLE_BOARD` 和 `CONFIG_CONSTRAINTS` 两个常量，并以此为基础启动app
'''

import numpy as np
from src.constraints import OrdArrowConstraint, KillerConstraint

# CONFIG_PUZZLE_BOARD = np.array([
#     [9, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 2, 0, 0, 1, 0, 0, 0, 3],
#     [0, 1, 0, 0, 0, 0, 0, 6, 0],
#     [0, 0, 0, 4, 0, 0, 0, 7, 0],
#     [7, 0, 8, 6, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 3, 0, 1, 0, 0],
#     [4, 0, 0, 0, 0, 0, 2, 0, 0]
# ])

# sum_pos_list = [(1,1), (1,2), (1,3), (1,4)]
# prod_pos_list = [(1,5)]
# oac = OrdArrowConstraint(sum_pos_list, prod_pos_list, prep_at_init=False)

# CONFIG_CONSTRAINTS = [oac]



CONFIG_PUZZLE_BOARD = np.array([
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

pos_list_1 = [(1,1), (1,2), (1,3), (2,3), (2,4), (2,5)]
killer_sum_1 = 26
kc1 = KillerConstraint(pos_list_1, killer_sum_1, prep_at_init=False)

pos_list_2 = [(1,8), (2,8)]
killer_sum_2 = 10
kc2 = KillerConstraint(pos_list_2, killer_sum_2, prep_at_init=False)

CONFIG_CONSTRAINTS = [kc1, kc2]
