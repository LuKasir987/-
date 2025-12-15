from typing import Any, Dict
from core.command import Command
from core.serializer import Serializer

class GameEventCommand(Command, Serializer['GameEventCommand']):
    """游戏事件基类，定义了游戏事件的基本接口"""
    from scene.game.game_scene import GameScene
    def __init__(self, frame: int, type: str):
        super().__init__(frame)
        self.type = type

    def execute(self, game_scene: 'GameScene'):
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame": self.frame,
            "type": self.type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameEventCommand':
        frame = data["frame"]
        type = data["type"]
        return cls(frame, type)
    
    @staticmethod
    def create_event_from_dict(data: Dict[str, Any]) -> 'GameEventCommand':
        """
        根据字典中的type字段创建对应的事件子类实例
        
        Args:
            data: 包含事件数据的字典
            
        Returns:
            对应的事件子类实例
        """
        event_type = data.get("type")
        if event_type == "move":
            return MoveEventCommand.from_dict(data)
        elif event_type == "rotate":
            return RotateEventCommand.from_dict(data)
        elif event_type == "lock_piece":
            return LockPieceEventCommand.from_dict(data)
        else:
            # 默认使用基类
            return GameEventCommand.from_dict(data)

class MoveEventCommand(GameEventCommand):
    from scene.game.game_scene import GameScene
    """移动事件"""
    def __init__(self, frame: int, dx: int, dy: int):
        super().__init__(frame, "move")
        self.dx = dx
        self.dy = dy

    def execute(self, game_scene: 'GameScene'):
        game_scene._try_move_piece(self.dx, self.dy)

    def to_dict(self) -> Dict[str, Any]:
            return {
                "frame": self.frame,
                "type": self.type,
                "dx": self.dx,
                "dy": self.dy
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoveEventCommand':
        frame = data["frame"]
        dx = data["dx"]
        dy = data["dy"]
        return cls(frame, dx, dy)
    
class RotateEventCommand(GameEventCommand):
    from scene.game.game_scene import GameScene
    """旋转事件"""
    def __init__(self, frame: int):
        super().__init__(frame, "rotate")

    def execute(self, game_scene: 'GameScene'):
        game_scene._try_rotate_piece()

    def to_dict(self) -> Dict[str, Any]:
            return {
                "frame": self.frame,
                "type": self.type,
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RotateEventCommand':
        frame = data["frame"]
        return cls(frame)

class LockPieceEventCommand(GameEventCommand):
    from scene.game.game_scene import GameScene
    """锁定事件"""
    def __init__(self, frame: int):
        super().__init__(frame, "lock_piece")

    def execute(self, game_scene: 'GameScene'):
        game_scene._lock_piece()

    def to_dict(self) -> Dict[str, Any]:
            return {
                "frame": self.frame,
                "type": self.type,
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LockPieceEventCommand':
        frame = data["frame"]
        return cls(frame)