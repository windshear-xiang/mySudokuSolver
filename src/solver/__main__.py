import numpy as np
from .sudoku import Sudoku
from ..constraints import KillerConstraint

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

pos_list_1 = [(1,1), (1,2), (1,3), (2,3), (2,4), (2,5)]
killer_sum_1 = 26
kc1 = KillerConstraint(pos_list_1, killer_sum_1)

pos_list_2 = [(1,8), (2,8)]
killer_sum_2 = 10
kc2 = KillerConstraint(pos_list_2, killer_sum_2)

s = Sudoku(puzzle, [kc1, kc2])
s.solve_true_candidates()
sc, ct = s.get_counter_stat()
print(f"\n求解完成. {sc}steps, {ct:.3f}s, {ct/sc*1000:.4f}ms/step")
print("\n".join(str(row) for row in s.print_true_candidates()))