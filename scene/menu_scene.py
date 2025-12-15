import os
from data.config import GameConfig
import pygame
from scene.scene import Scene
from ui.panel import Panel
from resources.resource_manager import ResId, ResourcesManager
from scene.scene_manager import SceneManager
from scene.game.game_replay_data import GameReplayData


class MenuScene(Scene):
    def __init__(self, name: str = "menu_scene"):
        super().__init__(name)

        # 菜单场景的初始化代码
        self.image_background = ResourcesManager().get_resource(ResId.MENU_BACKGROUND, (GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        
        # 创建菜单面板
        self.menu_panel_x = 0
        self.menu_panel_y = 290
        self.menu_panel_width = GameConfig.WINDOW_WIDTH // 2
        self.menu_panel_height = 610
        self.menu_panel = Panel(
            self.menu_panel_x, self.menu_panel_y,
            self.menu_panel_width, self.menu_panel_height,
            padding=230,
            spacing=30,
            font_size=24,
            res_id=None
        )

        # 创建菜单按钮
        self.menu_panel.add_button("开始游戏", self._start_game)
        self.menu_panel.add_button("继续游戏", self._continue_game)
        self.menu_panel.add_button("排行榜", self._show_rank_scene)
        self.menu_panel.add_button("操作说明", self._operation_instruction)
        self.menu_panel.add_button("退出游戏", self._exit_game)

        # 创建说明信息
        self.instruction_panel_text = (
            "操作说明：\n"
            "1. 使用WAD键控制俄罗斯方块移动和旋转\n"
            "2. 按下S键快速下降\n"
            "3. 按下空格键暂停游戏\n"
            "4. 游戏有自动存档功能，不用担心存档丢失哦~"
        )

    def _start_game(self):
        """开始游戏回调"""
        from scene.game.game_scene import GameScene
        from tkinter import messagebox
        if os.path.exists(GameConfig.SAVE_GAME_DATA_FILE_PATH):
            if not messagebox.askyesno("确认开始新游戏", "当前有保存的游戏数据，是否确认开始新游戏？"):
                return
        game_scene = GameScene()
        SceneManager().add_scene(game_scene)
        SceneManager().set_active_scene(game_scene.name)

    def _continue_game(self):
        """继续游戏回调"""
        from scene.game.game_scene import GameScene
        game_scene = GameScene()
        if game_scene.load_game_data(GameConfig.SAVE_GAME_DATA_FILE_PATH):
            SceneManager().add_scene(game_scene)
            SceneManager().set_active_scene(game_scene.name)
        else:
            from tkinter import messagebox
            messagebox.showinfo("信息", "文件不存在或加载游戏数据失败，将默认开始新游戏")
            game_scene = GameScene()
            SceneManager().add_scene(game_scene)
            SceneManager().set_active_scene(game_scene.name)

    def _show_rank_scene(self):
        """排行榜场景回调"""
        from scene.rank_scene import RankScene
        rank_scene = RankScene()
        SceneManager().add_scene(rank_scene)
        SceneManager().set_active_scene(rank_scene.name)
    
    def _get_replay_files(self):
        """获取所有重放文件"""
        import re
        replay_data_path = GameConfig.SAVE_GAME_REPLAY_DATA_FILE_PATH
        replay_files = []
        
        # 确保目录存在
        if not os.path.exists(replay_data_path):
            os.makedirs(replay_data_path, exist_ok=True)
            return replay_files
        
        # 遍历目录中的文件
        for file_name in os.listdir(replay_data_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(replay_data_path, file_name)
                # 检查是否是重放文件格式
                pattern = r"game_replay_data_(\d+)\.json"
                match = re.match(pattern, file_name)
                if match:
                    replay_files.append(file_path)
        
        return replay_files
    
    def _start_replay(self, file_path: str):
        """开始回放游戏"""
        from scene.game.game_scene import GameScene
        game_scene = GameScene()
        if game_scene.load_game_replay_data(file_path):
            SceneManager().add_scene(game_scene)
            SceneManager().set_active_scene(game_scene.name)
        else:
            from tkinter import messagebox
            messagebox.showerror("错误", "加载回放数据失败")

    def _operation_instruction(self):
        """操作说明回调"""
        from tkinter import messagebox
        messagebox.showinfo("操作说明", self.instruction_panel_text)
    
    def _exit_game(self):
        """退出游戏回调"""
        GameConfig.RUNNING = False
    
    def enter(self):
        pass
    
    def input(self, event):
        # 处理菜单面板事件
        self.menu_panel.handle_event(event)
    
    def update(self):
        pass
    
    def render(self):
        # 获取全局screen对象
        screen = pygame.display.get_surface()

        # 绘制背景
        screen.blit(self.image_background, (0, 0))

        # 绘制菜单面板
        self.menu_panel.render()

    def exit(self):
        pass