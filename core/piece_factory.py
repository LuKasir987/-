from data.piece import Piece
from data.tile import TileType
from core.singleton import Singleton
import random
import pickle
import base64

class PieceFactory(Singleton):
    # 类变量，用于存储随机数生成器
    _random_generator = random.Random()
    
    def set_seed(self, seed: int):
        """设置随机数种子，实现随机性的可复现"""
        self._random_generator.seed(seed)
    
    def get_random_state(self) -> str:
        """
        获取当前随机数生成器的状态，用于存档
        
        Returns:
            str: 序列化后的随机数生成器状态
        """
        try:
            # 获取随机数生成器的状态
            state = self._random_generator.getstate()
            # 使用pickle序列化状态
            serialized_state = pickle.dumps(state)
            # 使用base64编码，便于存储为字符串
            return base64.b64encode(serialized_state).decode('utf-8')
        except Exception as e:
            print(f"获取随机数状态失败: {e}")
            return ""
        
    def set_random_state(self, state_str: str) -> bool:
        """
        恢复随机数生成器的状态，用于读档
        
        Args:
            state_str (str): 序列化的随机数生成器状态
            
        Returns:
            bool: 是否成功恢复状态
        """
        try:
            # 从base64解码
            serialized_state = base64.b64decode(state_str.encode('utf-8'))
            # 反序列化状态
            state = pickle.loads(serialized_state)
            # 设置随机数生成器的状态
            self._random_generator.setstate(state)
            return True
        except Exception as e:
            print(f"恢复随机数状态失败: {e}")
            return False
    
    def create_random_piece(self, x: int, y: int) -> Piece: 
        """创建一个随机类型的俄罗斯方块"""
        # 从TileType枚举中随机选择一个类型 排除EMPTY WALL类型
        # 添加权重 使某些类型更常见
        tile_type_list = [t for t in TileType if t not in [TileType.EMPTY, TileType.WALL]]
        weights = [2, 2, 2, 1, 1, 1, 1]  # I, O, T更常见一些
        piece_type = self._random_generator.choices(tile_type_list, weights=weights)[0]
        return Piece(x, y, piece_type)
    
    @staticmethod
    def create_piece(x: int, y: int, type: TileType, rotation: int = 0) -> Piece:
        """创建指定类型的俄罗斯方块"""
        return Piece(x, y, type, rotation)
