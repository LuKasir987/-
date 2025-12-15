import os
import pygame
from scene.scene import Scene
from data.config import GameConfig
from resources.resource_manager import ResId, ResourcesManager
from ui.panel import Panel
from ui.button import Button, ButtonState
from scene.scene_manager import SceneManager
from scene.game.game_replay_data import GameReplayData


class RankScene(Scene):
    def __init__(self, name: str = "rank_scene"):
        super().__init__(name)
        
        # 背景图片
        self.background = ResourcesManager().get_resource(ResId.MENU_BACKGROUND, (GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        
        # 创建排行榜面板
        self.panel_width = 1200
        self.panel_height = 800
        self.panel_x = (GameConfig.WINDOW_WIDTH - self.panel_width) // 2
        self.panel_y = (GameConfig.WINDOW_HEIGHT - self.panel_height) // 2 - 50
        self.rank_panel = Panel(
            self.panel_x, self.panel_y,
            self.panel_width, self.panel_height,
            padding=50,
            spacing=20,
            font_size=16,
            res_id=ResId.PANEL
        )
        
        # 返回按钮
        self.back_button = Button(
            self.panel_x + (self.panel_width - 300) // 3, 
            self.panel_y + self.panel_height, 
            300, 80, 
            text="返回", 
            callback=self._back_to_menu
        )
        self.back_button.set_background_image(ButtonState.IDLE, ResId.BUTTON_IDLE)
        self.back_button.set_background_image(ButtonState.HOVERED, ResId.BUTTON_HOVERED)
        self.back_button.set_background_image(ButtonState.PRESSED, ResId.BUTTON_PRESSED)
        
        # 排行榜数据
        self.game_records = []
        self.selected_index = -1
        
        # 加载游戏记录
        self._load_game_records()
        
        # 创建回放按钮
        self.replay_button = Button(
            self.panel_x + (self.panel_width - 300) // 3 * 2 + 100,
            self.panel_y + self.panel_height,
            300, 80, 
            text="回放",
            callback=self._replay_selected
        )
        self.replay_button.set_background_image(ButtonState.IDLE, ResId.BUTTON_IDLE)
        self.replay_button.set_background_image(ButtonState.HOVERED, ResId.BUTTON_HOVERED)
        self.replay_button.set_background_image(ButtonState.PRESSED, ResId.BUTTON_PRESSED)
        
    
    def _load_game_records(self):
        """加载游戏记录"""
        import re
        
        replay_data_path = GameConfig.SAVE_GAME_REPLAY_DATA_FILE_PATH
        self.game_records = []
        
        # 确保目录存在
        if not os.path.exists(replay_data_path):
            os.makedirs(replay_data_path, exist_ok=True)
            return
        
        # 遍历目录中的文件
        for file_name in os.listdir(replay_data_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(replay_data_path, file_name)
                # 检查是否是重放文件格式
                pattern = r"game_replay_data_(\d+)\.json"
                match = re.match(pattern, file_name)
                if match:
                    try:
                        replay_data = GameReplayData.load_from_file(file_path)
                        if replay_data:
                            self.game_records.append({
                                'file_name': file_name,
                                'file_path': file_path,
                                'score': replay_data.score,
                                'game_time': replay_data.game_finished_time,
                                'start_date': replay_data.game_start_date
                            })
                    except Exception as e:
                        print(f"加载重放文件失败 {file_path}: {e}")
        
        # 按分数排序
        self.game_records.sort(key=lambda x: x['score'], reverse=True)
    
    
    def _back_to_menu(self):
        """返回主菜单"""
        from scene.menu_scene import MenuScene
        menu_scene = MenuScene()
        SceneManager().add_scene(menu_scene)
        SceneManager().set_active_scene(menu_scene.name)
    
    def _replay_selected(self):
        """回放选中的记录"""
        if 0 <= self.selected_index < len(self.game_records):
            selected_record = self.game_records[self.selected_index]
            file_path = selected_record['file_path']
            
            # 开始回放
            from scene.game.game_scene import GameScene
            game_scene = GameScene()
            if game_scene.load_game_replay_data(file_path):
                SceneManager().add_scene(game_scene)
                SceneManager().set_active_scene(game_scene.name)
    
    def enter(self):
        """进入场景"""
        pass
    
    def input(self, event):
        """处理输入事件"""
        # 处理返回按钮
        self.back_button.handle_event(event)
        
        # 处理回放按钮
        self.replay_button.handle_event(event)
        
        
        # 处理键盘选择
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
            elif event.key == pygame.K_DOWN:
                if self.selected_index < len(self.game_records) - 1:
                    self.selected_index += 1
            elif event.key == pygame.K_RETURN:
                self._replay_selected()
            elif event.key == pygame.K_ESCAPE:
                self._back_to_menu()
        
        # 处理鼠标点击选择记录
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_x, mouse_y = event.pos
                
                # 检查是否点击了记录区域
                record_area = pygame.Rect(
                    self.panel_x + 50,
                    self.panel_y + 100,
                    self.panel_width - 300,
                    len(self.game_records) * 40 if len(self.game_records) > 0 else 40
                )
                
                if record_area.collidepoint(mouse_x, mouse_y):
                    # 计算点击的记录索引
                    clicked_index = (mouse_y - record_area.y) // 40
                    if 0 <= clicked_index < len(self.game_records):
                        self.selected_index = clicked_index
    
    def update(self):
        """更新场景"""
        pass
    
    def render(self):
        """渲染场景"""
        screen = pygame.display.get_surface()
        
        # 绘制背景
        screen.blit(self.background, (0, 0))
        
        # 绘制面板
        self.rank_panel.render()
        
        # 绘制标题
        font = ResourcesManager().get_resource(ResId.FONT_STHUPO, 32)
        title_text = font.render("游戏排行榜", True, (235, 50, 35))  # 红色
        title_rect = title_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, self.panel_y + 30))
        screen.blit(title_text, title_rect)
        
        if not self.game_records:
            # 没有记录
            no_records_text = font.render("没有游戏记录", True, (0, 0, 0))  # 黑色
            no_records_rect = no_records_text.get_rect(center=(GameConfig.WINDOW_WIDTH // 2, GameConfig.WINDOW_HEIGHT // 2))
            screen.blit(no_records_text, no_records_rect)
        else:
            # 绘制表头
            header_font = ResourcesManager().get_resource(ResId.FONT_STHUPO, 20)
            headers = ["排名", "分数", "游戏时间", "开始日期"]
            header_x = self.panel_x + 180
            header_y = self.panel_y + 80
            
            for i, header in enumerate(headers):
                header_text = header_font.render(header, True, (0, 0, 0))  # 黑色
                screen.blit(header_text, (header_x + i * 180, header_y))
            
            # 绘制记录
            record_font = ResourcesManager().get_resource(ResId.FONT_STHUPO, 18)
            
            for i, record in enumerate(self.game_records):
                rank = i + 1
                score = record['score']
                game_time = record['game_time'] if record['game_time'] else "未完成"
                start_date = record['start_date']
                
                # 计算位置
                y = self.panel_y + 120 + i * 40
                
                # 高亮选中的记录
                if i == self.selected_index:
                    highlight_rect = pygame.Rect(self.panel_x + 50, y - 5, self.panel_width - 100, 35)
                    pygame.draw.rect(screen, (200, 200, 200), highlight_rect)
                    pygame.draw.rect(screen, (100, 100, 100), highlight_rect, 2)
                
                # 绘制记录信息
                rank_text = record_font.render(str(rank), True, (0, 0, 0))
                score_text = record_font.render(str(score), True, (0, 0, 0))
                time_text = record_font.render(game_time, True, (0, 0, 0))
                date_text = record_font.render(start_date, True, (0, 0, 0))
                
                screen.blit(rank_text, (header_x, y))
                screen.blit(score_text, (header_x + 180, y))
                screen.blit(time_text, (header_x + 360, y))
                screen.blit(date_text, (header_x + 540, y))
        
        # 绘制按钮
        self.back_button.render()
        self.replay_button.render()
        
    
    def exit(self):
        """退出场景"""
        pass