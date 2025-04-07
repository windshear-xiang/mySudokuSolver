from src.config import CONFIG_PUZZLE_BOARD, CONFIG_CONSTRAINTS
from src.ui.controller import SudokuController

app = SudokuController(CONFIG_PUZZLE_BOARD, CONFIG_CONSTRAINTS)
app.view.root.mainloop()
