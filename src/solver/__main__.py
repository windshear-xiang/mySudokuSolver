import numpy as np
from .sudoku import Sudoku
from ..constraints import KillerConstraint, OrdArrowConstraint

puzzle = np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 1, 0, 0, 0, 3],
    [0, 1, 0, 0, 0, 0, 0, 6, 0],
    [0, 0, 0, 4, 0, 0, 0, 7, 0],
    [7, 0, 8, 6, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 3, 0, 1, 0, 0],
    [4, 0, 0, 0, 0, 0, 2, 0, 0]
])

cells = [[2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6]]
params = {"prod_len" : 3}
oac = OrdArrowConstraint(cells, params)

s = Sudoku(puzzle, [oac])
s.solve_true_candidates()
sc, ct = s.get_counter_stat()
print(f"\n求解完成. {sc}steps, {ct:.3f}s, {ct/sc*1000:.4f}ms/step")
print("\n".join(str(row) for row in s.print_true_candidates()))