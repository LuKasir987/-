from typing import Any, Dict
from data.config import GameConfig
from core.serializer import Serializer
from scene.game.game_event import GameEventCommand
import os

class GameReplayData(Serializer['GameReplayData']):
    """游戏重放数据"""
    def __init__(self,
                map_size: tuple[int, int],
                game_start_date: str, 
                game_finished_time: str = "",
                file_index: int = 0,
                score: int = 0,
                game_seed: int = 0,
                event_queue: list[GameEventCommand] = []):
        self.map_size = map_size
        self.game_start_date = game_start_date
        self.game_finished_time = game_finished_time
        self.file_index = file_index
        self.score = score
        self.game_seed = game_seed
        self.event_queue = event_queue

    @classmethod
    def from_game_scene(cls, game_scene) -> 'GameReplayData':
        file_index = 0
        with os.scandir(GameConfig.SAVE_GAME_REPLAY_DATA_FILE_PATH) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".json"):
                    file_index += 1

        return cls(
            map_size=[game_scene.map.width, game_scene.map.height],
            game_start_date=game_scene.game_start_date,
            game_finished_time=game_scene.game_frame_counter.get_time_parts(),
            file_index=file_index,
            score=game_scene.score,
            game_seed=game_scene.game_seed,
            event_queue=list(game_scene.event_queue)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "map_size": self.map_size,
            "game_start_date": self.game_start_date,
            "game_finished_time": self.game_finished_time,
            "file_index": self.file_index,
            "score": self.score,
            "game_seed": self.game_seed,
            "events": [event.to_dict() for event in self.event_queue]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameReplayData':
        # 使用GameEventCommand的静态方法创建事件实例
        return cls(
            map_size=data["map_size"],
            game_start_date=data["game_start_date"],
            game_finished_time=data["game_finished_time"],
            file_index=data["file_index"],
            score=data["score"],
            game_seed=data["game_seed"],
            event_queue=[GameEventCommand.create_event_from_dict(event_data) for event_data in data["events"]]
        )
