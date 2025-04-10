import numpy as np
from src.config import CONFIG_PUZZLE_BOARD, CONFIG_CONSTRAINTS
from src.ui.controller import SudokuController

app = SudokuController(
    np.asarray(CONFIG_PUZZLE_BOARD, dtype=np.int8),
    CONFIG_CONSTRAINTS
)
app.view.root.mainloop()
