# 游戏配置
import pygame
import sys
import os

def get_resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和打包环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class GameConfig:
    # 游戏帧率
    FPS = 60

    RUNNING = True
    # 适配16寸屏幕
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 900

    # 方块大小
    TILE_SIZE = 40

    # 方块下降速度
    MOVE_DOWN_INTERVAL = 750  # 方块下落间隔时间（毫秒）
    # 方块加速下降速度
    MOVE_DOWN_INTERVAL_ACCEL = 50  # 加速下落间隔时间（毫秒）
    # 方块水平移动速度
    MOVE_SIDE_INTERVAL = 50  # 水平移动间隔时间（毫秒）
    # 方块旋转速度
    ROTATE_INTERVAL = 150  # 旋转间隔时间（毫秒）

    # 保存文件路径
    SAVE_GAME_DATA_FILE_PATH = get_resource_path("saves/game_data.json")
    # 游戏重放数据文件夹路径
    SAVE_GAME_REPLAY_DATA_FILE_PATH = get_resource_path("saves/replay_json/")
    # 游戏重放数据文件名格式
    SAVE_GAME_REPLAY_DATA_FILE_NAME = "game_replay_data_{}.json"

    AUTO_SAVE_INTERVAL = 30000  # 自动保存间隔时间（毫秒）
