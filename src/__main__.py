from src.config import CONFIG_PUZZLE_BOARD, CONFIG_CONSTRAINTS
from src.ui.controller import SudokuController

ui = SudokuController()
ui.model.curr_puzzle_board = CONFIG_PUZZLE_BOARD
ui.model.constraints = CONFIG_CONSTRAINTS
ui.view.root.mainloop()
