"""
Tile类 - 表示地图网格中的单个方块
"""
from enum import Enum
from typing import Dict, Any
from core.serializer import Serializer


class TileType(Enum):
    """方块类型枚举"""
    EMPTY = "TILE_EMPTY"      # 空白
    WALL = "TILE_WALL"   # 墙壁
    # 已固定的方块类型，对应piece.py中的类型名称
    I = "TILE_I"
    O = "TILE_O"
    T = "TILE_T"
    L = "TILE_L"
    J = "TILE_J"
    S = "TILE_S"
    Z = "TILE_Z"


class Tile(Serializer['Tile']):
    """表示地图网格中的单个方块"""
    
    def __init__(self, tile_type: TileType = TileType.EMPTY):
        """
        初始化Tile对象
        
        Args:
            tile_type: 方块类型，默认为空白
        """
        self.tile_type = tile_type
    
    def set_type(self, tile_type: TileType) -> None:
        """设置方块类型"""
        self.tile_type = tile_type
    
    def get_type(self) -> TileType:
        """获取方块类型"""
        return self.tile_type
    
    def is_empty(self) -> bool:
        """检查方块是否为空"""
        return self.tile_type == TileType.EMPTY
    
    def is_wall(self) -> bool:
        """检查方块是否为墙壁"""
        return self.tile_type == TileType.WALL
    
    def is_block(self) -> bool:
        """检查方块是否为已固定的方块"""
        return not self.is_empty() and not self.is_wall()
    
    def to_dict(self) -> Dict[str, Any]:
        """将Tile对象转换为字典，用于序列化"""
        return {
            'tile_type': self.tile_type.name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tile':
        """从字典创建Tile对象，用于反序列化"""
        # 从字符串值获取枚举类型
        tile_type_str = data.get('tile_type', TileType.EMPTY.name)
        try:
            tile_type = TileType[tile_type_str]
        except ValueError:
            tile_type = TileType.EMPTY
            
        return cls(tile_type=tile_type)
    
    def __eq__(self, other) -> bool:
        """比较两个Tile对象是否相等"""
        if not isinstance(other, Tile):
            return False
        return self.tile_type == other.tile_type