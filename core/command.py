class Command:
    """命令基类，定义了命令的基本接口"""
    def __init__(self, frame: int):
        self.frame = frame

    def execute(self):
        pass