from data.config import GameConfig
from typing import Dict, Any
from core.serializer import Serializer

class GameFrameCounter(Serializer['GameFrameCounter']):
    """游戏帧计时器，用于记录游戏运行时间"""
    def __init__(self, frame_count: int = 0, fps: int = GameConfig.FPS):
        self.frame_count = frame_count
        self.fps = fps
        self.seconds_per_frame = 1.0 / self.fps

    def tick(self):
        """更新游戏帧计数"""
        self.frame_count += 1

    def total_seconds(self) -> int:
        """获取游戏总秒数"""
        return int(self.frame_count * self.seconds_per_frame)
    
    def reset(self):
        """重置游戏帧计数"""
        self.frame_count = 0

    def hours(self) -> int:
        """获取游戏当前小时数"""
        return self.total_seconds() // 3600 % 24
    
    def minutes(self) -> int:
        """获取游戏当前分钟数"""
        return self.total_seconds() // 60 % 60
    
    def seconds(self) -> int:
        """获取游戏当前秒数"""
        return self.total_seconds() % 60
    
    def get_time_parts(self) -> str:
        """获取时间部分，格式为HH:MM:SS，过滤掉前导的0时间部分"""
        hours = self.hours()
        minutes = self.minutes()
        seconds = self.seconds()
        
        # 构建时间部分，从小时开始，如果小时为0则不显示
        time_parts = []
        if hours > 0:
            time_parts.append(f"{hours:02d}")
        if minutes > 0 or hours > 0:
            time_parts.append(f"{minutes:02d}")
        time_parts.append(f"{seconds:02d}")
        
        return ":".join(time_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """将GameFrameCounter对象转换为字典，用于序列化"""
        return {
            'frame_count': self.frame_count,
            'fps': self.fps
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameFrameCounter':
        """从字典创建GameFrameCounter对象，用于反序列化"""
        return cls(
            frame_count=data.get('frame_count', 0),
            fps=data.get('fps', GameConfig.FPS)
        )
