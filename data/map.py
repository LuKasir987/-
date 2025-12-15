import os
from typing import List, Dict, Any, Optional, Tuple

import pygame

from resources.resource_manager import ResourcesManager, ResId
from .tile import Tile, TileType
from core.serializer import Serializer
from .config import GameConfig

class Map(Serializer['Map']):
    """存储游戏地图网格数据的类"""
    
    def __init__(self, width: int = 30, height: int = 20, tile_size: int = GameConfig.TILE_SIZE):
        """
        初始化Map对象
        
        Args:
            width: 地图宽度（网格数）
            height: 地图高度（网格数）
            tile_size: 方块大小（像素）"""
        self.width = width
        self.height = height
        self.tile_map: List[List[Tile]] = [[Tile() for _ in range(width)] for _ in range(height)]
        self.tile_map_dirty: List[List[bool]] = [[True for _ in range(width)] for _ in range(height)]  # 地图网格是否需要重绘
        self.tile_size = tile_size
        self.texture = pygame.Surface((self.width * self.tile_size, self.height * self.tile_size)).convert_alpha()
        self.texture.fill((0, 0, 0, 0))  # 透明背景
        
        self.initialize_map()
    
    def initialize_map(self) -> None:
        """初始化地图网格"""
        # 创建边界墙壁
        for x in range(self.width):
            self.set_tile(x, self.height - 1, TileType.WALL)  # 下边界
        
        for y in range(self.height):
            self.set_tile(0, y, TileType.WALL)  # 左边界
            self.set_tile(self.width - 1, y, TileType.WALL)  # 右边界
        
        for y in range(self.height):
            for x in range(self.width):
                if not self.get_tile(x, y).is_wall():
                    self.set_tile(x, y, TileType.EMPTY)
        
    def create_map_texture(self) -> None:
        """创建地图的纹理"""
        resources_manager = ResourcesManager()
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile(x, y)
                if tile and self.tile_map_dirty[y][x]:
                    x_pos, y_pos = self.map_position_to_screen_position(x, y)
                    self.tile_map_dirty[y][x] = False
                    self.texture.fill((0, 0, 0, 0), (x_pos, y_pos, self.tile_size, self.tile_size))
                    try:
                        tile_img = resources_manager.get_resource(ResId[tile.get_type().value], (self.tile_size, self.tile_size), alpha_val=200)
                        if tile.is_empty():
                            tile_img.set_alpha(50)  # 设置透明度
                        
                        self.texture.blit(tile_img, (x_pos, y_pos))
                    except Exception:
                        print(f"无法加载方块资源: {tile.get_type().name}")
                        pygame.draw.rect(self.texture, (255, 0, 0), 
                                    (x_pos, y_pos, self.tile_size, self.tile_size))
    
    def check_and_clear_lines(self) -> int:
        """检查并清除满行方块，返回清除的行数"""
        clear_count = 0
        for y in range(self.height - 2, -1, -1):
            if all(not tile.is_empty() for tile in self.tile_map[y]):
                # 清除满行 忽略边界墙壁
                for x in range(1, self.width - 1):
                    self.set_tile(x, y, TileType.EMPTY)
                clear_count += 1
            else:
                # 下移行
                for x in range(1, self.width - 1):
                    if y + clear_count < self.height:
                        self.set_tile(x, y + clear_count, self.tile_map[y][x].get_type())
        return clear_count
    
    def map_position_to_screen_position(self, x: int, y: int) -> Tuple[int, int]:
        """将地图坐标转换为屏幕坐标"""
        # 直接计算坐标，不检查边界，支持越界坐标
        return (x * self.tile_size, y * self.tile_size)
    
    def screen_position_to_map_position(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """将屏幕坐标转换为地图坐标"""
        if 0 <= x < self.width * self.tile_size and 0 <= y < self.height * self.tile_size:
            return (x // self.tile_size, y // self.tile_size)
        return None

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """
        获取指定位置的方块
        Returns:
            指定位置的Tile对象，如果坐标超出范围则返回None
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tile_map[y][x]
        return None
    
    def set_tile(self, x: int, y: int, tile_type: TileType) -> bool:
        """设置指定位置的方块类型 如果目标类型与原类型不同则修改方块类型 且标记为脏"""
        if 0 <= x < self.width and 0 <= y < self.height:
            if tile_type == self.tile_map[y][x].get_type():
                return False
            self.tile_map_dirty[y][x] = True
            self.tile_map[y][x].set_type(tile_type)
            return True
        return False
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """检查坐标是否在地图范围内"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_wall_range_position(self, x: int, y: int) -> bool:
        """检查坐标是否在墙壁范围内"""
        return 0 < x < self.width - 1 and 0 < y < self.height - 1
    
    def to_dict(self) -> Dict[str, Any]:
        """将Map对象转换为字典，用于序列化"""
        tile_map_data = []
        for y in range(self.height):
            row_data = []
            for x in range(self.width):
                row_data.append(self.tile_map[y][x].to_dict())
            tile_map_data.append(row_data)
        
        return {
            'width': self.width,
            'height': self.height,
            'tile_map': tile_map_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Map':
        """从字典创建Map对象，用于反序列化"""
        map_obj = cls(
            width=data.get('width', 20),
            height=data.get('height', 20)
        )
        
        tile_map_data = data.get('tile_map', [])
        for y, row_data in enumerate(tile_map_data):
            if y >= map_obj.height:
                break
            for x, tile_data in enumerate(row_data):
                if x >= map_obj.width:
                    break
                map_obj.tile_map[y][x] = Tile.from_dict(tile_data)
        
        return map_obj
