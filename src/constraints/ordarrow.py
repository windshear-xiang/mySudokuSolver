from src.utils.ordinal import Ordinal
from . import DenseMultiCellConstraint

class OrdArrowConstraint(DenseMultiCellConstraint):
    def __init__(self, sum_pos_list: list, prod_pos_list: list):
        self.sum_len = len(sum_pos_list)
        super().__init__(sum_pos_list + prod_pos_list)

    @property
    def sum_pos_list(self):
        return self.cell_positions[0:self.sum_len]
    
    @property
    def prod_pos_list(self):
        return self.cell_positions[self.sum_len:]
    
    def is_valid(self, assigned_board):
        board_sum = 0
        board_prod = 1
        for (i,j) in self.sum_pos_list:
            if assigned_board[i][j] == 0:
                return True
            else:
                board_sum += Ordinal.digit2ord(assigned_board[i][j])
        for (i,j) in self.prod_pos_list:
            if assigned_board[i][j] == 0:
                return True
            else:
                board_prod *= Ordinal.digit2ord(assigned_board[i][j])
        return board_sum == board_prod
    