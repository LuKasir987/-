# core/piece.py
from dataclasses import dataclass
from data.tile import TileType
from typing import List, Tuple, Dict, Any
from core.serializer import Serializer

# 定义俄罗斯方块的相对形状
PIECE = {
    TileType.I: [
        [(0,2), (0,1), (0,0), (0,-1)],
        [(-2,0), (-1,0), (0,0), (1,0)]
    ],
    TileType.O: [
        [(0,0), (-1,0), (0,1), (-1,1)]
    ],
    TileType.T: [
        [(-1,0), (0,0), (1,0), (0,1)],
        [(0,1), (0,0), (0,-1), (1,0)],
        [(-1,0), (0,0), (1,0), (0,-1)],
        [(0,1), (0,0), (0,-1), (-1,0)]
    ],
    TileType.Z: [
        [(0,0), (1,0), (1,1), (0,-1)],
        [(0,0), (-1,0), (0,-1), (1,-1)]
    ],
    TileType.S: [
        [(0,0), (1,0), (1,-1), (0,1)],
        [(0,0), (0,-1), (-1,-1), (1,0)]
    ],
    TileType.J: [
        [(-1,-1), (0,0), (0,1), (0,-1)],
        [(-1,1), (0,0), (-1,0), (1,0)],
        [(1,1), (0,0), (0,1), (0,-1)],
        [(1,-1), (0,0), (-1,0), (1,0)]
    ],
    TileType.L: [
        [(1,-1), (0,0), (0,1), (0,-1)],
        [(-1,-1), (0,0), (-1,0), (1,0)],
        [(-1,1), (0,0), (0,1), (0,-1)],
        [(1,1), (0,0), (-1,0), (1,0)]
    ]
}
class Piece(Serializer['Piece']):
    def __init__(self, x, y, type: TileType, rotation: int = 0):
        self.x = x
        self.y = y
        self.type = type
        self.rotation = rotation

    def shape(self) -> List[Tuple[int, int]]: 
        """获取当前旋转状态下的方块形状"""
        return PIECE[self.type][self.rotation]
    
    def rotate(self):
        """顺时针旋转方块"""
        self.rotation = (self.rotation + 1) % len(PIECE[self.type])

    def rotate_counterclockwise(self):
        """逆时针旋转方块"""
        self.rotation = (self.rotation - 1) % len(PIECE[self.type])

    def get_block_positions(self) -> List[Tuple[int, int]]:
        """返回当前方块在地图上的所有坐标位置"""
        return [(self.x + dx, self.y - dy) for dx, dy in self.shape()]
    
    def move(self, dx: int, dy: int):
        """移动方块位置"""
        self.x += dx
        self.y += dy
    
    def to_dict(self) -> Dict[str, Any]:
        """将Piece对象转换为字典，用于序列化"""
        return {
            'x': self.x,
            'y': self.y,
            'type': self.type.name,
            'rotation': self.rotation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Piece':
        """从字典创建Piece对象，用于反序列化"""
        # 从字符串值获取枚举类型
        type_str = data.get('type', TileType.I.name)
        try:
            piece_type = TileType[type_str]
        except (KeyError, ValueError):
            piece_type = TileType.I  # 默认类型
            
        return cls(
            x=data.get('x', 0),
            y=data.get('y', 0),
            type=piece_type,
            rotation=data.get('rotation', 0)
        )