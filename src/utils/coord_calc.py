"""这个模块会读取 `config.py` 里的 `BOARD_SIDE_LENGTH`，以此为参数，根据单元格在哪个格子，计算 canvas 上的坐标
"""

from src.ui_config import BOARD_SIDE_LENGTH, SIDE_PANEL_WIDTH

def calc_left_top(i: int, j: int):
    """计算单元格在 board_canvas 上的左上角坐标，注意 x,y 和 i,j 的横竖是反过来的"""
    x0 = j * BOARD_SIDE_LENGTH
    y0 = i * BOARD_SIDE_LENGTH
    return x0, y0

def calc_right_bottom(i: int, j: int):
    """计算单元格在 board_canvas 上的右下角坐标，注意 x,y 和 i,j 的横竖是反过来的"""
    x0 = j * BOARD_SIDE_LENGTH
    y0 = i * BOARD_SIDE_LENGTH
    x1 = x0 + BOARD_SIDE_LENGTH
    y1 = y0 + BOARD_SIDE_LENGTH
    return x1, y1

def calc_center(i: int, j: int):
    """计算单元格在 board_canvas 上的中心坐标，注意 x,y 和 i,j 的横竖是反过来的"""
    x0 = j * BOARD_SIDE_LENGTH
    y0 = i * BOARD_SIDE_LENGTH
    center_x = x0 + BOARD_SIDE_LENGTH // 2
    center_y = y0 + BOARD_SIDE_LENGTH // 2
    return center_x, center_y
