"""视图层

Passive view 没有控制层调用就啥也不干，组件的回调函数也都写在控制层。
"""

import numpy as np
import tkinter as tk
from src.utils.ordinal import digit2ord
from src.ui.logger import Logger
from src.ui.ui_config import BOARD_SIDE_LENGTH, SIDE_PANEL_WIDTH
from src.utils.coord_calc import *
from src.utils.type_definitions import *

DIGIT_TO_ORD_STR = {n: str(digit2ord(n)) for n in range(1, 10)}

class SudokuView:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Sudoku Solver")

        # 日志生成器
        self.raw_logger = Logger(self._log_append)
        self.log = self.raw_logger("view")

        # 视图层状态属性
        self.display_as_ord_var = tk.BooleanVar(value=False) # 序数显示模式

         # 构建棋盘及其它控件
        self._build_board()
        self._build_side_panel()

        # 可对外提供接口，绑定事件处理程序
        self.event_callbacks = {}
    
    def _log_append(self, message: str):
        """
        将日志信息追加到日志显示框中。
        为了线程安全，这里用 after 方法在主线程中更新 Text 控件
        """
        def append():
            self.log_text.configure(state=tk.NORMAL) # 切换为可写入状态
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state=tk.DISABLED) # 还原为不可写入状态
        self.root.after(0, append)

    def handle_event(self, event_type, *args):
        """视图层收集事件，再转发给 Controller 的事件处理函数"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type](*args)
        else:
            self.log(f"ERROR: event_type={event_type} args={args} cannot be handled.")

    def bind_event(self, event_type, callback):
        """供 Controller 注册各类事件处理函数"""
        self.event_callbacks[event_type] = callback
    
    def _build_board(self):
        """创建单一 Canvas 用于绘制整个数独棋盘"""
        board_size = 9 * BOARD_SIDE_LENGTH  # 例如 9 * 90 = 810
        self.board_canvas = tk.Canvas(self.root, width=board_size, height=board_size, bg="white", highlightthickness=0)
        # 将棋盘 Canvas 放在主界面左侧（例如：grid(row=0, column=0)）
        self.board_canvas.grid(row=0, column=0, padx=0, pady=0)
        self.board_canvas.bind("<Button-1>", self._on_board_click)
    
    def _on_board_click(self, event):
        """
        根据鼠标点击的坐标计算所在单元格 (i, j)
        然后调用 handle_event 通知 Controller 进行处理。
        """
        col = event.x // BOARD_SIDE_LENGTH
        row = event.y // BOARD_SIDE_LENGTH
        self.handle_event("cell_click", row, col)
    
    def _build_side_panel(self):
        """创建右侧控制面板"""
        self.side_frame = tk.Frame(self.root)
        self.side_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        # 在 side_frame 顶部创建一个控制区（control_frame）用于放置勾选框和按钮
        self.control_frame = tk.Frame(self.side_frame)
        self.control_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

        # 自动求解的勾选框【注意这个放在控制层了】
        self.auto_solve_cb = tk.Checkbutton(self.control_frame, text="Auto Solve")
        self.auto_solve_cb.grid(row=0, column=0, padx=5)

        # 序数显示的勾选框
        self.display_as_ord_cb = tk.Checkbutton(self.control_frame, text="Display as Ordinal", variable=self.display_as_ord_var)
        self.display_as_ord_cb.grid(row=0, column=1, padx=5)

        # 求解的按钮
        self.solve_button = tk.Button(self.control_frame, text="Solve True Candidates", command=lambda: self.handle_event("start_solver"))
        self.solve_button.grid(row=1, column=0, padx=5, pady=5)

        # 强行停止求解的按钮
        self.stop_button = tk.Button(self.control_frame, text="Force Stop", command=lambda: self.handle_event("stop_solver"))
        self.stop_button.grid(row=1, column=1, padx=5, pady=5)

        # 在控制区下方增加一行，用于 "Save" 和 "Load" 按钮
        self.sl_frame = tk.Frame(self.control_frame)
        self.sl_frame.grid(row=2, column=0, padx=5, pady=5)

        self.save_button = tk.Button(self.sl_frame, text="Save", command=lambda: self.handle_event("save"))
        self.save_button.grid(row=0, column=0, padx=5, pady=5)

        self.load_button = tk.Button(self.sl_frame, text="Load", command=lambda: self.handle_event("load"))
        self.load_button.grid(row=0, column=1, padx=5, pady=5)

        # 撤销和恢复
        self.unredo_frame = tk.Frame(self.control_frame)
        self.unredo_frame.grid(row=2, column=1, padx=5, pady=5)

        self.undo_button = tk.Button(self.unredo_frame, text="Undo", command=lambda: self.handle_event("undo"))
        self.undo_button.grid(row=0, column=0, padx=5, pady=5)

        self.redo_button = tk.Button(self.unredo_frame, text="Redo", command=lambda: self.handle_event("redo"))
        self.redo_button.grid(row=0, column=1, padx=5, pady=5)

        # 日志显示框（用于显示文字信息）
        self.log_label = tk.Label(self.side_frame, text="LOG")
        self.log_label.pack(side=tk.TOP, anchor='w', padx=5, pady=(15, 0))
        self.log_text = tk.Text(self.side_frame, width=SIDE_PANEL_WIDTH, height=18, state=tk.DISABLED)
        self.log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # constraints 显示框，放在日志显示框下面
        self.constraint_label_frame = tk.Frame(self.side_frame, width=SIDE_PANEL_WIDTH)
        self.constraint_label_frame.pack(side=tk.TOP, anchor='w', padx=5, pady=(15, 0))

        self.constraint_label = tk.Label(self.constraint_label_frame, text="Constraints")
        self.constraint_label.grid(row=0, column=0, padx=5, pady=5)

        self.new_constraint_button = tk.Button(self.constraint_label_frame, text="New", command=lambda: self.handle_event("new_constraint"))
        self.new_constraint_button.grid(row=0, column=1, padx=5, pady=5)

        self.constraint_container = tk.Frame(self.side_frame, width=SIDE_PANEL_WIDTH, height=18, borderwidth=1, relief="groove")
        self.constraint_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_display(self,
            curr_puzzle_board: NumBoard,
            curr_tuf_board: TufBoard,
            constraints: list,
            selected_cell: Position | None,
            constraint_cells: list,
            config_constraint_index: int | None
        ):
        """在单一 Canvas 上绘制整个棋盘内容"""
        # 清除上一次的绘制
        self.board_canvas.delete("all")
        # 画单元格边框
        for i in range(9):
            for j in range(9):
                self._draw_cell_borders(i, j)
        # 画约束规则的显示
        self._draw_constraints(
            constraints,
            config_constraint_index
        )
        # 绘制单元格内容
        for i in range(9):
            for j in range(9):
                self._draw_cell_content(i, j, curr_puzzle_board, curr_tuf_board, selected_cell)
        # 绘制 constraint cells 内容
        for index, (i, j) in enumerate(constraint_cells):
            self._draw_constraint_cell(i, j, index)
    
    def _draw_constraints(self, constraints, config_constraint_index: int | None):
        for index, constraint in enumerate(constraints):
            constraint.draw(self.board_canvas)

    def _draw_constraint_cell(self, i, j, index):
        x0, y0 = calc_left_top(i, j)
        x1, y1 = calc_right_bottom(i, j)
        center_x , center_y = calc_center(i, j)
        self.board_canvas.create_rectangle(
            x0, y0, x1, y1, fill="magenta", outline="", stipple="gray75"
        )
        self.board_canvas.create_text(
            center_x, center_y, text=str(index), font=('Arial', 60), fill='white'
        )

    def _draw_cell_content(self, i: int, j: int, curr_puzzle_board, curr_tuf_board, selected_cell):
        """绘制单元格内容"""
        # 计算单元格在 board_canvas 上的坐标
        x0, y0 = calc_left_top(i, j)
        center_x , center_y = calc_center(i, j)

        if curr_puzzle_board[i, j] != 0:
            # 已经 assigned 的格子：画黑色大数字
            self._draw_assigned_number(center_x, center_y, curr_puzzle_board[i, j])
        else:
            cell_data = curr_tuf_board[i, j]
            true_cand_count = np.sum(cell_data == 1)
            false_cand_count = np.sum(cell_data == -1)
            if true_cand_count == 1 and false_cand_count == 8:
                # 已确定的格子：画蓝色大数字
                num = int(np.argmax(cell_data) + 1)
                self._draw_big_number(center_x, center_y, num)
            else:
                # 未确定：绘制候选信息
                self._draw_small_grid(x0, y0, cell_data)
        # 绘制选框
        if selected_cell == (i, j):
            self._highlight_cell(x0, y0)

    def _draw_cell_borders(self, i: int, j: int):
        # 计算单元格在 board_canvas 上的左上角坐标和右下角坐标
        (x0, y0), (x1, y1) = calc_left_top(i, j), calc_right_bottom(i, j)
        
        # 绘制细边线
        self.board_canvas.create_line(x0, y0, x0, y1, width=1, fill='#cccccc')
        self.board_canvas.create_line(x0, y0, x1, y0, width=1, fill='#cccccc')
        self.board_canvas.create_line(x1 - 1, y0, x1 - 1, y1, width=1, fill='#cccccc')
        self.board_canvas.create_line(x0, y1 - 1, x1, y1 - 1, width=1, fill='#cccccc')
        
        # 绘制粗边线来突出 3x3 分块
        if j % 3 == 0:
            self.board_canvas.create_line(x0, y0, x0, y1, width=2)
        if i % 3 == 0:
            self.board_canvas.create_line(x0, y0, x1, y0, width=2)
        if j % 3 == 2:
            self.board_canvas.create_line(x1 - 1, y0, x1 - 1, y1, width=2)
        if i % 3 == 2:
            self.board_canvas.create_line(x0, y1 - 1, x1, y1 - 1, width=2)
    
    def _highlight_cell(self, x0: int, y0: int):
        x1 = x0 + BOARD_SIDE_LENGTH
        y1 = y0 + BOARD_SIDE_LENGTH
        self.board_canvas.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2, outline="red", width=3)
    
    def _draw_assigned_number(self, center_x: int, center_y: int, number: int):
        if self.display_as_ord_var.get():
            self.board_canvas.create_text(center_x, center_y, text=DIGIT_TO_ORD_STR[number], font=('Arial', 26), fill='black')
        else:
            self.board_canvas.create_text(center_x, center_y, text=str(number), font=('Arial', 40), fill='black')
    
    def _draw_big_number(self, center_x: int, center_y: int, number: int):
        if self.display_as_ord_var.get():
            self.board_canvas.create_text(center_x, center_y, text=DIGIT_TO_ORD_STR[number], font=('Arial', 26), fill='blue')
        else:
            self.board_canvas.create_text(center_x, center_y, text=str(number), font=('Arial', 40), fill='blue')
        
    def _draw_small_grid(self, x0: int, y0: int, cell_data: np.ndarray):
        # 无解情况
        if np.all(cell_data == -1):
            self.board_canvas.create_text(x0 + BOARD_SIDE_LENGTH // 2, y0 + BOARD_SIDE_LENGTH // 2,
                                          text='X', font=('Arial', BOARD_SIDE_LENGTH // 2), fill='red')
            return
        for num in range(1, 10):
            idx = num - 1
            state = cell_data[idx]
            row = (num - 1) // 3
            col = (num - 1) % 3
            # 计算小数字在该单元格内的位置，注意相对于该单元格的 x0, y0
            x = x0 + col * (BOARD_SIDE_LENGTH // 3) + (BOARD_SIDE_LENGTH // 6)
            y = y0 + row * (BOARD_SIDE_LENGTH // 3) + (BOARD_SIDE_LENGTH // 6)
            if state == -1:
                color = 'white'
                continue
            elif state == 1:
                color = 'blue'
            else:
                color = 'green' # '#cccccc'
            if self.display_as_ord_var.get():
                if num == 8:
                    x += 5
                self.board_canvas.create_text(x + 3, y + 3,
                                              text=DIGIT_TO_ORD_STR[num],
                                              font=('Arial', 9), fill=color)
            else:
                self.board_canvas.create_text(x, y,
                                              text=str(num),
                                              font=('Arial', 12), fill=color)

    def refresh_constraints_panel(self,
            constraint_dicts: list[dict],
            config_constraint_index: int | None
        ):
        # 先清空原有内容
        for old_widget in self.constraint_container.winfo_children():
            old_widget.destroy()

        if len(constraint_dicts) == 0:
            empty_label = tk.Label(self.constraint_container, text="None.")
            empty_label.pack(fill=tk.X, padx=2, pady=2)
            return

        for index, c_dict in enumerate(constraint_dicts):
            # 为每个约束创建一个子 Frame，其内包含约束描述、参数输入框、修改和删除按钮
            row_frame = tk.Frame(self.constraint_container, borderwidth=1, relief="sunken")
            row_frame.pack(fill=tk.X, padx=2, pady=2)

            if index == config_constraint_index:
                self._build_config_constraint_row(row_frame, c_dict, index)
            else:
                self._build_normal_constraint_row(row_frame, c_dict, index)
    
        return
    
    def _build_config_constraint_row(self, row_frame: tk.Frame, constraint_dict: dict, index: int):

        constraint_name = constraint_dict["name"]
        constraint_info = "Configuring..."
        constraint_params = constraint_dict["params"]

        # 放 label 和 config / delete button
        label_button_frame = tk.Frame(row_frame)
        label_button_frame.pack(side=tk.TOP, fill=tk.X)
        # Label 显示约束描述
        name_label = tk.Label(
            label_button_frame,
            anchor="w",
            text=f"C{index}: " + constraint_name)
        name_label.pack(side=tk.LEFT, padx=2, pady=2)
        # 取消按钮，退出config状态
        cancel_button = tk.Button(
            label_button_frame,
            text="Cancel",
            command=lambda index=index: self.handle_event("exit_config_constraint")
        )
        cancel_button.pack(side=tk.RIGHT, padx=2, pady=2)
        # confirm按钮
        confirm_button = tk.Button(
            label_button_frame,
            text="Confirm",
            command=lambda index=index: self.handle_event("confirm_config_constraint", index)
        )
        confirm_button.pack(side=tk.RIGHT, padx=2, pady=2)

        # 显示 info
        info_label = tk.Label(
            row_frame,
            width=SIDE_PANEL_WIDTH - 10,
            anchor="w",
            text=constraint_info)
        info_label.pack(fill=tk.X, padx=2, pady=2)

        # 显示 param
        for key, var in constraint_params.items():
            param_frame = tk.Frame(row_frame)
            param_frame.pack(side=tk.TOP, fill=tk.X)
            # param label
            param_label = tk.Label(param_frame, text=f"{key} = ")
            param_label.grid(row=0, column=0, pady=2)
            # param entry
            param_entry = tk.Entry(
                param_frame,
                textvariable=var,
                width=20)
            param_entry.grid(row=0, column=1, pady=2)

    def _build_normal_constraint_row(self, row_frame: tk.Frame, constraint_dict: dict, index: int):
        constraint_name = constraint_dict["name"]
        constraint_info = constraint_dict["info"]

        # 放 label 和 config / delete button
        label_button_frame = tk.Frame(row_frame)
        label_button_frame.pack(side=tk.TOP, fill=tk.X)
        # Label 显示约束描述
        name_label = tk.Label(
            label_button_frame,
            anchor="w",
            text=f"C{index}: " + constraint_name)
        name_label.pack(side=tk.LEFT, padx=2, pady=2)
        # 删除按钮，点击后调用 handle_event 并传入对应约束的id
        delete_button = tk.Button(
            label_button_frame,
            text="Del",
            command=lambda index=index: self.handle_event("delete_constraint", index)
        )
        delete_button.pack(side=tk.RIGHT, padx=2, pady=2)
        # config按钮
        config_button = tk.Button(
            label_button_frame,
            text="Config",
            command=lambda index=index: self.handle_event("enter_config_constraint", index)
        )
        config_button.pack(side=tk.RIGHT, padx=2, pady=2)

        # 显示 info
        info_label = tk.Label(
            row_frame,
            width=SIDE_PANEL_WIDTH - 10,
            anchor="w",
            text=constraint_info)
        info_label.pack(fill=tk.X, padx=2, pady=2)



    # def on_add_constraint_clicked(self):
    #     """
    #     当点击添加约束按钮时，由 Controller 提供当前可用的约束列表，
    #     这里为了示例直接使用一个假定的列表，后续 Controller 可调用 view.show_add_constraint_dialog(available_list, callback)
    #     """
    #     available_constraints = ["ConstraintA", "ConstraintB", "ConstraintC"]
    #     # 此处传入的 callback 函数将在用户点击确认后被调用
    #     self.show_add_constraint_dialog(available_constraints, self.handle_new_constraint)
    
    # def show_add_constraint_dialog(self, available_constraints: list, callback):
    #     """
    #     弹出一个对话框供用户选择约束类型和输入参数。
        
    #     参数:
    #       available_constraints: 一个约束名称列表，填充在下拉选框中。
    #       callback: 当用户点击确认时调用此方法，传入用户选择的约束类型和参数。
    #     """
    #     dialog = tk.Toplevel(self.root)
    #     dialog.title("Add Constraint")
    #     dialog.grab_set()  # 模态对话框，使用户在关闭对话框前无法点击主窗口

    #     # 约束类型的下拉选框
    #     tk.Label(dialog, text="Constraint Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    #     constraint_type = tk.StringVar(value=available_constraints[0])
    #     option_menu = tk.OptionMenu(dialog, constraint_type, *available_constraints)
    #     option_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
    #     # 参数的文本输入框
    #     tk.Label(dialog, text="Parameters:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    #     param_entry = tk.Entry(dialog, width=30)
    #     param_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
    #     # 确认按钮
    #     def on_confirm():
    #         sel_type = constraint_type.get()
    #         params = param_entry.get().strip()
    #         # 调用传入的回调函数，将选中的约束类型和参数传递出去
    #         callback(sel_type, params)
    #         dialog.destroy()  # 关闭对话框
        
    #     confirm_button = tk.Button(dialog, text="Confirm", command=on_confirm)
    #     confirm_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10)
    
    # def handle_new_constraint(self, constraint_type: str, params: str):
    #     """
    #     这个方法作为回调函数，在用户确认添加约束后被调用。
    #     你可以在这里调用 Controller 提供的事件接口，传递用户选择的 constraint_type 和 params。
    #     """
    #     self.handle_event("add_constraint", constraint_type, params)
    #     print(f"Add constraint: {constraint_type} with params: {params}")