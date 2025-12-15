from scene.game.game_event import GameEventCommand
from core.piece_factory import PieceFactory
from scene.game.game_frame_counter import GameFrameCounter
from data.map import Map
from data.piece import Piece
from core.serializer import Serializer
from typing import Optional, Dict, List, Any

class GameData(Serializer['GameData']):
    """游戏数据类，负责游戏状态的序列化和反序列化"""
    
    def __init__(self,
                map: Optional[Map] = None,
                random_state: Optional[str] = None,
                game_seed: Optional[int] = None,
                score: int = 0,
                current_piece: Optional[Piece] = None,
                next_piece_queue: Optional[List[Piece]] = None,
                game_frame_counter: Optional[GameFrameCounter] = None,
                event_queue: Optional[List[GameEventCommand]] = None,
                game_start_date: Optional[str] = None):
        """
        初始化GameData对象
        
        Args:
            map: 游戏地图
            random_state: 随机数状态
            game_seed: 游戏种子
            score: 游戏分数
            current_piece: 当前方块对象
            next_piece_queue: 下一个方块队列
            game_frame_counter: 游戏帧计数器
            event_queue: 游戏事件队列
            game_start_date: 游戏开始日期
        """
        self.map = map
        self.random_state = random_state
        self.game_seed = game_seed
        self.score = score
        self.current_piece = current_piece
        self.next_piece_queue = next_piece_queue or []
        self.game_frame_counter = game_frame_counter or GameFrameCounter()
        self.event_queue = event_queue or []
        self.game_start_date = game_start_date
    
    @classmethod
    def from_game_scene(cls, game_scene) -> 'GameData':
        """从GameScene对象创建GameData对象"""
        # 直接使用Piece对象，利用其自身的序列化方法
        current_piece = game_scene.current_piece
        
        # 获取下一个方块队列
        next_piece_queue = list(game_scene.next_piece_queue) if game_scene.next_piece_queue else []
        # 获取游戏事件队列
        event_queue = list(game_scene.event_queue) if game_scene.event_queue else []
        
        return cls(
            map=game_scene.map,
            random_state=PieceFactory().get_random_state(),
            game_seed=game_scene.game_seed,
            score=game_scene.score,
            current_piece=current_piece,
            next_piece_queue=next_piece_queue,
            game_frame_counter=game_scene.game_frame_counter,
            event_queue=event_queue,
            game_start_date=game_scene.game_start_date
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """将GameData对象转换为字典，用于序列化"""
        return {
            'map': self.map.to_dict() if self.map else None,
            'random_state': self.random_state,
            'game_seed': self.game_seed,
            'score': self.score,
            'current_piece': self.current_piece.to_dict() if self.current_piece else None,
            'next_piece_queue': [piece.to_dict() for piece in self.next_piece_queue] if self.next_piece_queue else [],
            'game_frame_counter': self.game_frame_counter.to_dict() if self.game_frame_counter else None,
            'event_queue': [event.to_dict() for event in self.event_queue] if self.event_queue else [],
            'game_start_date': self.game_start_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameData':
        """从字典创建GameData对象，用于反序列化"""
        # 使用GameEventCommand的静态方法创建事件实例
        return cls(
            map=Map.from_dict(data['map']) if data.get('map') else None,
            random_state=data.get('random_state'),
            game_seed=data.get('game_seed'),
            score=data.get('score', 0),
            current_piece=Piece.from_dict(data['current_piece']) if data.get('current_piece') else None,
            next_piece_queue=[Piece.from_dict(piece_data) for piece_data in data['next_piece_queue']] if data.get('next_piece_queue') else [],
            game_frame_counter=GameFrameCounter.from_dict(data['game_frame_counter']) if data.get('game_frame_counter') else None,
            event_queue=[GameEventCommand.create_event_from_dict(event_data) for event_data in data.get('event_queue', [])],
            game_start_date=data.get('game_start_date')
        )
