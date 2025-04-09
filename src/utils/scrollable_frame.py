""" 自带滚动条的 Frame 容器 """

import tkinter as tk

class ScrollableFrame(tk.Frame):
    """ 自带滚动条的 Frame 容器 """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 创建 Canvas（无滚动条）
        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            width=kwargs.get("width", 200)  # 强制固定宽度（与原容器一致）
        )
        self.inner_frame = tk.Frame(self.canvas)
        
        # 将 inner_frame 嵌入 Canvas
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # 动态约束宽度（关键）
        self.inner_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._update_canvas_width)
        
        # 绑定鼠标滚轮实现滚动（隐藏滚动条但保留功能）
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # 布局 Canvas（占满父容器）
        self.canvas.pack(side="left", fill="both", expand=True)
    
    def _update_scroll_region(self, event=None):
        """ 更新滚动范围（禁止无限滚动） """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _update_canvas_width(self, event):
        """ 强制内部容器宽度与 Canvas 一致 """
        self.canvas.itemconfig("all", width=event.width)
    
    def _on_mousewheel(self, event):
        """ 鼠标滚轮滚动逻辑 """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")