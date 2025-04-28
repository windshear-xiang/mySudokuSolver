'''
主程序会读取这里定义的 `CONFIG_PUZZLE_BOARD` 和 `CONFIG_CONSTRAINTS` 两个常量，并以此为基础启动app
'''

import numpy as np
from src.constraints import OrdArrowConstraint, KillerConstraint

# CONFIG_PUZZLE_BOARD = np.array([
#         [0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 0, 0, 0, 0, 0],
#         [0, 2, 0, 0, 1, 0, 0, 0, 3],
#         [0, 1, 0, 0, 0, 0, 0, 6, 0],
#         [0, 0, 0, 4, 0, 0, 0, 7, 0],
#         [7, 0, 8, 6, 0, 0, 0, 0, 0],
#         [0, 0, 0, 0, 3, 0, 1, 0, 0],
#         [4, 0, 0, 0, 0, 0, 2, 0, 0]
#     ])

# cells1 = [[2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6]]
# params1 = {"prod_len" : 3}
# oac1 = OrdArrowConstraint(cells1, params1)

# cells2 = [[0, 0], [2, 0], [3, 0], [4, 0]]
# params2 = {"prod_len" : 2}
# oac2 = OrdArrowConstraint(cells2, params2)

# CONFIG_CONSTRAINTS = [oac1, oac2]


CONFIG_PUZZLE_BOARD = np.zeros((9, 9))
CONFIG_CONSTRAINTS = []
