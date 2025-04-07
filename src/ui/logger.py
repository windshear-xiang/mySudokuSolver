"""可以标注来源的日志生成器
"""

class Logger:
    """可以标注来源的日志生成器"""
    def __init__(self, log_append_func) -> None:
        self.log_append_func = log_append_func
    
    def __call__(self, source: str):
        def sourced_logger(msg: str):
            self.log_append_func(f"[{source}]: {msg}")
        return sourced_logger