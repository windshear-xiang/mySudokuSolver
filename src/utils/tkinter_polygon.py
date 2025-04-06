"""这个模块提供了一些在 tkinter 的 canvas 上绘制复杂多边形的整合函数
"""

import math
import tkinter as tk

def create_cutted_rectangle(canvas: tk.Canvas,
                            x0: float, y0: float, x1: float, y1: float,
                            cut_top: bool, cut_bottom: bool, cut_left: bool, cut_right: bool,
                            pad: float,
                            *args, **kwargs):
    points = []
    points.append((x0 + pad, y0 + pad))
    if not cut_top:
        points.append((x0 + pad, y0))
        points.append((x1 - pad, y0))
    points.append((x1 - pad, y0 + pad))
    if not cut_right:
        points.append((x1, y0 + pad))
        points.append((x1, y1 - pad))
    points.append((x1 - pad, y1 - pad))
    if not cut_bottom:
        points.append((x1 - pad, y1))
        points.append((x0 + pad, y1))
    points.append((x0 + pad, y1 - pad))
    if not cut_left:
        points.append((x0, y1 - pad))
        points.append((x0, y0 + pad))
    return canvas.create_polygon(points, *args, **kwargs)

def create_approx_circle(canvas: tk.Canvas, center_x, center_y, radius, num_points=24, *args, **kwargs):
    """因为 **可爱** 的 tkinter 在 windows 上不支持椭圆形的 stipple 渲染，只好手工用多边形模拟一个
    """
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.extend([x, y])
    return canvas.create_polygon(points, *args, **kwargs)