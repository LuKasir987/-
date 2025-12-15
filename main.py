import pygame
import tkinter as tk
import sys
import os
from data.config import GameConfig
from scene.scene_manager import SceneManager
from scene.menu_scene import MenuScene
from resources.resource_manager import ResourcesManager, ResId

def get_resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和打包环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def ensure_save_directory():
    """确保存档目录存在"""
    save_dir = get_resource_path("saves/")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    replay_dir = os.path.join(save_dir, "replay_json/")
    if not os.path.exists(replay_dir):
        os.makedirs(replay_dir)

# 初始化pygame
pygame.init()

# 初始化Tkinter
root = tk.Tk()
root.withdraw()

# 设置窗口大小
screen = pygame.display.set_mode((GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 创建时钟对象用于控制帧率
clock = pygame.time.Clock()

# 初始化管理器
ResourcesManager().load_all()
menu_scene = MenuScene()
SceneManager().add_scene(menu_scene)
SceneManager().set_active_scene(menu_scene.name)

# 确保存档目录存在
ensure_save_directory()

# 初始化音乐
pygame.mixer.init()
# 播放背景音乐
pygame.mixer.music.load(get_resource_path("resources/" + ResId.MUSIC_MAIN.value))
pygame.mixer.music.play(loops=-1, fade_ms=1000)

# 游戏主循环
while GameConfig.RUNNING:
    # 控制帧率为60FPS
    clock.tick(GameConfig.FPS)
    
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GameConfig.RUNNING = False
        SceneManager().input(event)
    # 更新场景
    SceneManager().update()
    # 渲染场景
    screen.fill((0, 0, 0))
    SceneManager().render()
    # 更新显示
    pygame.display.flip()

# 退出pygame
pygame.quit()

# 退出Tkinter
root.destroy()