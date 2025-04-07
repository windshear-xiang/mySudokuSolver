from src.config import CONFIG_PUZZLE_BOARD, CONFIG_CONSTRAINTS
from src.ui.controller import SudokuController

ui = SudokuController(CONFIG_PUZZLE_BOARD, CONFIG_CONSTRAINTS)
ui.view.root.mainloop()
