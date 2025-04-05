from src.config import BOARD_SIDE_LENGTH, SIDE_PANEL_WIDTH

def calc_left_top(i: int, j: int):
    """计算单元格在 board_canvas 上的左上角坐标"""
    x0 = j * BOARD_SIDE_LENGTH
    y0 = i * BOARD_SIDE_LENGTH
    return x0, y0

def calc_right_bottom(i: int, j: int):
    """计算单元格在 board_canvas 上的右下角坐标"""
    x0 = j * BOARD_SIDE_LENGTH
    y0 = i * BOARD_SIDE_LENGTH
    x1 = x0 + BOARD_SIDE_LENGTH
    y1 = y0 + BOARD_SIDE_LENGTH
    return x1, y1

def calc_center(i: int, j: int):
    """计算单元格在 board_canvas 上的中心坐标"""
    x0 = j * BOARD_SIDE_LENGTH
    y0 = i * BOARD_SIDE_LENGTH
    center_x = x0 + BOARD_SIDE_LENGTH // 2
    center_y = y0 + BOARD_SIDE_LENGTH // 2
    return center_x, center_y
