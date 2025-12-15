from collections import deque
import os
import pygame
from scene.scene import Scene
from data.config import GameConfig
from resources.resource_manager import ResId, ResourcesManager
from typing import Optional, Tuple
from data.map import Map
from core.piece_factory import PieceFactory
from core.random_seed_generator import RandomSeedGenerator
from tools.timer import Timer
from scene.game.game_frame_counter import GameFrameCounter
from ui.panel import Panel
from scene.scene_manager import SceneManager


class GameScene(Scene):
    def __init__(self, name: str = "game_scene"):
        super().__init__(name)

        self.game_background = ResourcesManager().get_resource(ResId.GAME_BACKGROUND, (GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT))
        self.is_game_over = False
        self.is_game_paused = False
        self.is_replay = False
        self.is_replay_over = False
        self.is_replay_paused = False

    def _init(self):
        """初始化游戏场景"""
        # 初始化游戏分数
        if not hasattr(self, 'score'):
            self.score = 0
        # 初始化游戏开始日期
        if not hasattr(self, 'game_start_date'):
            from datetime import datetime
            self.game_start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 初始化游戏帧计数器
        if not hasattr(self, 'game_frame_counter'):
            self.game_frame_counter = GameFrameCounter()
        # 初始化地图
        if not hasattr(self, 'map'):
            self.map = Map()
        # 初始化游戏种子
        if not hasattr(self, 'game_seed'):
            self.game_seed = RandomSeedGenerator.generate_seed()
            PieceFactory().set_seed(self.game_seed)
        # 创建当前方块
        self.current_piece_dx = self.map.width // 2
        self.current_piece_dy = 0
        if not hasattr(self, 'current_piece'):
            self.current_piece = PieceFactory().create_random_piece(self.current_piece_dx, self.current_piece_dy)
        # 初始化方块预览队列
        if not hasattr(self, 'next_piece_queue'):
            self.next_piece_length = self.map.height // 5
            self.next_piece_queue = deque()
            self.next_piece_queue.extend([PieceFactory().create_random_piece(self.current_piece_dx, self.current_piece_dy) for _ in range(self.next_piece_length)])

        # 初始化事件队列
        if not hasattr(self, 'event_queue'):
            from scene.game.game_event import GameEventCommand
            self.event_queue: deque[GameEventCommand] = deque()

        # 创建地图纹理
        self.map.create_map_texture()
        self.map_x = (GameConfig.WINDOW_WIDTH - self.map.width * GameConfig.TILE_SIZE) // 2
        self.map_y = (GameConfig.WINDOW_HEIGHT - self.map.height * GameConfig.TILE_SIZE) // 2 + GameConfig.TILE_SIZE

        # 初始化定时器
        # 用于控制方块下落
        self.move_down_timer = Timer(GameConfig.MOVE_DOWN_INTERVAL, lambda: self._try_move_piece(0, 1, self._lock_piece))
        self.move_down_timer.start()
        # 用于控制方块持续左右移动
        self.is_move_left = False
        self.move_left_timer = Timer(GameConfig.MOVE_SIDE_INTERVAL, lambda: self._try_move_piece(-1, 0))
        self.move_left_timer.start()
        # 用于控制方块持续左右移动
        self.is_move_right = False
        self.move_right_timer = Timer(GameConfig.MOVE_SIDE_INTERVAL, lambda: self._try_move_piece(1, 0))
        self.move_right_timer.start()
        # 用于控制方块持续旋转
        self.is_rotate = False
        self.rotate_timer = Timer(GameConfig.ROTATE_INTERVAL, lambda: self._try_rotate_piece())
        self.rotate_timer.start()
        # 自动保存游戏状态
        self.auto_save_timer = Timer(GameConfig.AUTO_SAVE_INTERVAL, lambda: self._save_game_data(GameConfig.SAVE_GAME_DATA_FILE_PATH))
        self.auto_save_timer.start()

        # 初始化游戏UI元素
        # 方块预览位置放在地图右侧
        self.next_piece_dx = self.map.width + 1
        self.next_piece_dy = 1

        # 分数显示位置
        self.score_dx = self.map.width // 3
        self.score_dy = -1

        # 时间的显示位置
        self.game_frame_counter_dx = self.map.width // 3 * 2
        self.game_frame_counter_dy = -1

        # 游戏结束提示框
        self.game_over_panel_width = 600
        self.game_over_panel_height = 600
        self.game_over_panel = Panel(
            GameConfig.WINDOW_WIDTH // 2 - self.game_over_panel_width // 2,
            GameConfig.WINDOW_HEIGHT // 2 - self.game_over_panel_height // 2,
            self.game_over_panel_width, self.game_over_panel_height,
            75, 100
        )

        # 添加重新开始和退出游戏按钮
        self.game_over_panel.add_button("重新开始", self._handle_restart_game)
        self.game_over_panel.add_button("返回主菜单", self._handle_return_to_menu)

        # 游戏暂停提示框
        self.pause_panel_width = 600
        self.pause_panel_height = 600
        self.pause_panel = Panel(
            GameConfig.WINDOW_WIDTH // 2 - self.pause_panel_width // 2,
            GameConfig.WINDOW_HEIGHT // 2 - self.pause_panel_height // 2,
            self.pause_panel_width, self.pause_panel_height,
            75, 100
        )
        self.pause_panel.add_button("继续游戏", self._handle_resume_game)
        self.pause_panel.add_button("保存并返回主菜单", self._handle_save_and_return_to_menu)

        # 添加游戏重放暂停面板
        self.replay_pause_panel_width = 600
        self.replay_pause_panel_height = 600
        self.replay_pause_panel = Panel(
            GameConfig.WINDOW_WIDTH // 2 - self.replay_pause_panel_width // 2,
            GameConfig.WINDOW_HEIGHT // 2 - self.replay_pause_panel_height // 2,
            self.replay_pause_panel_width, self.replay_pause_panel_height,
            75, 100
        )
        self.replay_pause_panel.add_button("继续回放", self._handle_resume_replay_game)
        self.replay_pause_panel.add_button("返回主菜单", self._handle_return_to_menu)

        # 添加游戏重放结束面板
        self.replay_over_panel_width = 600
        self.replay_over_panel_height = 600
        self.replay_over_panel = Panel(
            GameConfig.WINDOW_WIDTH // 2 - self.replay_over_panel_width // 2,
            GameConfig.WINDOW_HEIGHT // 2 - self.replay_over_panel_height // 2,
            self.replay_over_panel_width, self.replay_over_panel_height,
            75, 100
        )
        self.replay_over_panel.add_button("重新开始回放", self._handle_restart_replay_game)
        self.replay_over_panel.add_button("返回主菜单", self._handle_return_to_menu)

    def _save_game_data(self, file_path: str) -> bool:
        """保存游戏状态到指定文件
        Args:
            file_path (str): (Default: GameConfig.SAVE_GAME_DATA_FILE_PATH)
        """
        from scene.game.game_data import GameData
        game_data = GameData.from_game_scene(self)
        if game_data is None:
            print(f"从游戏场景创建游戏数据失败：{file_path}")
            return False
        return game_data.save_to_file(file_path)

    def _save_game_replay_data(self, file_path: str) -> bool:
        """保存游戏重放状态到指定文件
        Args:
            file_path (str): (Default: GameConfig.SAVE_GAME_REPLAY_DATA_FILE_PATH)
        """
        from scene.game.game_replay_data import GameReplayData
        
        game_replay_data = GameReplayData.from_game_scene(self)
        if game_replay_data is None:
            print(f"从游戏场景创建游戏重放数据失败：{file_path}")
            return False
        
        # 构建完整的文件路径
        full_file_path = os.path.join(file_path, GameConfig.SAVE_GAME_REPLAY_DATA_FILE_NAME.format(game_replay_data.file_index))
        if not game_replay_data.save_to_file(full_file_path):
            return False
        
        if game_replay_data.file_index > 9:
            print(f"游戏重放数据文件索引超出范围：{game_replay_data.file_index}，已删除最旧文件")
            delete_oldest_file = os.path.join(file_path, GameConfig.SAVE_GAME_REPLAY_DATA_FILE_NAME.format(0))
            if os.path.exists(delete_oldest_file):
                os.remove(delete_oldest_file)

            file_list = [f for f in os.listdir(file_path) if f.endswith(".json")]
            file_list.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
            for i, file_name in enumerate(file_list):
                # 重命名文件，将索引重新排序为从0开始
                print(f"重命名文件：{file_name} 为 {GameConfig.SAVE_GAME_REPLAY_DATA_FILE_NAME.format(i)}")
                os.rename(os.path.join(file_path, file_name), os.path.join(file_path, GameConfig.SAVE_GAME_REPLAY_DATA_FILE_NAME.format(i)))
        return True

    def load_game_data(self, file_path: str) -> bool:
        """从指定文件加载游戏状态
        Args:
            file_path (str): (Default: GameConfig.SAVE_GAME_DATA_FILE_PATH)
        """
        from scene.game.game_data import GameData
        game_data = GameData.load_from_file(file_path)
        if game_data is None:
            print(f"加载游戏数据失败：{file_path}")
            return False
        
        # 恢复游戏地图和状态
        if game_data.map is not None:
            self.map = game_data.map
        else:
            print("游戏数据中没有地图，加载失败")
            return False
        
        # 恢复随机数种子和随机数状态
        if game_data.game_seed is not None:
            self.game_seed = game_data.game_seed
            PieceFactory().set_seed(self.game_seed)
        else:
            print("游戏数据中没有随机数种子，加载失败")
            return False
        if game_data.random_state is not None:
            PieceFactory().set_random_state(game_data.random_state)
        else:
            print("游戏数据中没有随机数状态，加载失败")
            return False
        
        # 恢复游戏分数
        if game_data.score is not None:
            self.score = game_data.score
        else:
            print("游戏数据中没有分数，加载失败")
            return False
        
        # 恢复当前方块
        if game_data.current_piece is not None:
            self.current_piece = game_data.current_piece
        else:
            print("游戏数据中没有当前方块，加载失败")
            return False
        
        # 恢复方块预览队列
        if game_data.next_piece_queue is not None:
            self.next_piece_queue = deque(game_data.next_piece_queue)
            self.next_piece_length = len(self.next_piece_queue)
        else:
            print("游戏数据中没有方块预览队列，加载失败")
            return False

        # 恢复游戏帧计数器
        if game_data.game_frame_counter is not None:
            self.game_frame_counter = game_data.game_frame_counter
        else:
            print("游戏数据中没有游戏帧计数器，加载失败")
            return False
        
        # 恢复游戏事件队列
        if game_data.event_queue is not None:
            self.event_queue = deque(game_data.event_queue)
        else:
            print("游戏数据中没有游戏事件队列，加载失败")
            return False

        return True

    def load_game_replay_data(self, file_path: str) -> bool:
        """从指定文件加载游戏重放数据
        Args:
            file_path (str): (Default: GameConfig.SAVE_GAME_REPLAY_DATA_FILE_PATH + GameConfig.SAVE_GAME_REPLAY_DATA_FILE_NAME.format(file_index))
        """
        from scene.game.game_replay_data import GameReplayData
        self.is_replay = True
        self.current_replay_file_path = file_path  # 保存当前重放文件路径
        game_replay_data = GameReplayData.load_from_file(file_path)
        if game_replay_data is None:
            print(f"加载游戏重放数据失败：{file_path}")
            return False
        
        # 恢复游戏地图大小
        if game_replay_data.map_size is not None:
            self.map = Map(game_replay_data.map_size[0], game_replay_data.map_size[1])
        else:
            print("游戏重放数据中没有地图，加载失败")
            return False
        # 恢复游戏开始日期
        if game_replay_data.game_start_date is not None:
            self.game_start_date = game_replay_data.game_start_date
        else:
            print("游戏重放数据中没有开始日期，加载失败")
            return False
        # 恢复随机数种子
        if game_replay_data.game_seed is not None:
            self.game_seed = game_replay_data.game_seed
            PieceFactory().set_seed(self.game_seed)
        else:
            print("游戏重放数据中没有随机数种子，加载失败")
            return False
        # 恢复游戏事件队列
        if game_replay_data.event_queue is not None:
            self.event_queue = deque(game_replay_data.event_queue)
        else:
            print("游戏重放数据中没有游戏事件队列，加载失败")
            return False
        
        return True

    def _remove_save_game_data(self):
        """删除保存的游戏数据文件"""
        if os.path.exists(GameConfig.SAVE_GAME_DATA_FILE_PATH):
            os.remove(GameConfig.SAVE_GAME_DATA_FILE_PATH)

    def _try_move_piece(self, dx: int, dy: int, callback: Optional[callable] = None):
        """尝试移动当前方块"""
        if self.current_piece:
            self.current_piece.move(dx, dy)
            for x, y in self.current_piece.get_block_positions():
                tile = self.map.get_tile(x, y)
                if tile and not tile.is_empty():
                    self.current_piece.move(-dx, -dy)  # 撤销移动
                    if callback:
                        callback()
                    return False
            if not self.is_replay:
                from scene.game.game_event import MoveEventCommand
                self.event_queue.append(MoveEventCommand(self.game_frame_counter.frame_count, dx, dy))
            
            return True
        return False

    def _try_rotate_piece(self):
        """尝试旋转当前方块"""
        if self.current_piece:
            self.current_piece.rotate()
            for x, y in self.current_piece.get_block_positions():
                tile = self.map.get_tile(x, y)
                if tile and not tile.is_empty():
                    self.current_piece.rotate_counterclockwise()  # 撤销旋转
                    return False
            if not self.is_replay:
                from scene.game.game_event import RotateEventCommand
                self.event_queue.append(RotateEventCommand(self.game_frame_counter.frame_count))

            return True
        return False

    def _lock_piece(self):
        """锁定当前方块到地图"""
        if not self.is_replay:
            from scene.game.game_event import LockPieceEventCommand
            self.event_queue.append(LockPieceEventCommand(self.game_frame_counter.frame_count))
        if self.current_piece:
            for x, y in self.current_piece.get_block_positions():
                # 方块超出顶部，游戏结束 且不是重放模式
                if y == 0 and not self.is_replay:
                    self._game_over()
                self.map.set_tile(x, y, self.current_piece.type)
            # 游戏结束 或 重放模式下 不再生成新的方块
            if self.is_game_over or self.is_replay_over:
                return
            
            self.current_piece = self.next_piece_queue.popleft()
            self.next_piece_queue.append(PieceFactory().create_random_piece(self.current_piece_dx, self.current_piece_dy))
            # 检查并清除完整的行
            clear_count = self.map.check_and_clear_lines()
            # 更新分数
            if clear_count > 0:
                self.score += clear_count * 100
            
            # 重新创建地图纹理
            self.map.create_map_texture()

    def _handle_restart_game(self):
        """处理重新开始游戏按钮点击"""
        # 重置游戏状态
        self.score = 0
        self.map.initialize_map()
        self.map.create_map_texture()
        self.game_seed = RandomSeedGenerator.generate_seed()
        PieceFactory().set_seed(self.game_seed)
        self.current_piece = PieceFactory().create_random_piece(self.current_piece_dx, self.current_piece_dy)
        self.next_piece_queue = deque()
        self.next_piece_queue.extend([PieceFactory().create_random_piece(self.current_piece_dx, self.current_piece_dy) for _ in range(self.next_piece_length)])
        self.game_frame_counter.reset()
        from datetime import datetime
        self.game_start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.event_queue.clear()

        self.move_down_timer.reset()
        self.move_left_timer.reset()
        self.move_right_timer.reset()
        self.rotate_timer.reset()
        self.auto_save_timer.reset()

        self.move_down_timer.start()
        self.move_left_timer.start()
        self.move_right_timer.start()
        self.rotate_timer.start()
        self.auto_save_timer.start()
        
        self.is_game_over = False

    def _handle_return_to_menu(self):
        """处理返回主菜单按钮点击"""
        from scene.menu_scene import MenuScene
        menu_scene = MenuScene()
        SceneManager().add_scene(menu_scene)
        SceneManager().set_active_scene(menu_scene.name)

    def _handle_resume_game(self):
        """处理继续游戏按钮点击"""
        self.is_game_paused = False

    def _handle_save_and_return_to_menu(self):
        """处理保存并返回主菜单按钮点击"""
        self._save_game_data(GameConfig.SAVE_GAME_DATA_FILE_PATH)
        self._handle_return_to_menu()
    
    def _handle_resume_replay_game(self):
        """处理继续回放按钮点击"""
        self.is_replay_paused = False
    
    def _handle_restart_replay_game(self):
        """处理重新开始回放按钮点击"""
        # 重新加载当前重放文件
        if hasattr(self, 'current_replay_file_path'):
            self.load_game_replay_data(self.current_replay_file_path)
            self.is_replay_paused = False
            self.is_replay_over = False
            self.game_frame_counter.reset()
            self.score = 0
            self.map.create_map_texture()
            self.current_piece = PieceFactory().create_random_piece(self.current_piece_dx, self.current_piece_dy)
            self.next_piece_queue = deque()
            self.next_piece_queue.extend([PieceFactory().create_random_piece(self.current_piece_dx, self.current_piece_dy) for _ in range(self.next_piece_length)])
            self.game_frame_counter.reset()
        else:
            print("重复失败：当前没有重放文件")

    def _game_over(self):
        """处理游戏结束逻辑"""
        self.is_game_over = True
        self.move_down_timer.stop()
        self.move_left_timer.stop()
        self.move_right_timer.stop()
        self.rotate_timer.stop()
        self.auto_save_timer.stop()
        self._remove_save_game_data()
        self._save_game_replay_data(GameConfig.SAVE_GAME_REPLAY_DATA_FILE_PATH)

    def _game_replay_update(self):
        """处理游戏重放更新逻辑"""
        if self.is_replay_paused:
            return
        self.game_frame_counter.tick()
        while len(self.event_queue) > 0 and self.event_queue[0].frame <= self.game_frame_counter.frame_count:
            event = self.event_queue.popleft()
            event.execute(self)
        if len(self.event_queue) == 0:
            self.is_replay_over = True

    def _game_replay_input(self, event):
        """处理游戏重放输入逻辑"""
        if self.is_replay_paused:
            self.replay_pause_panel.handle_event(event)
        if self.is_replay_over:
            self.replay_over_panel.handle_event(event)
            
        if event.type == pygame.KEYDOWN:
            if self.is_replay_paused or self.is_replay_over:
                return
                
            if event.key == pygame.K_SPACE:
                self.is_replay_paused = True
            elif event.key == pygame.K_ESCAPE:
                self._handle_return_to_menu()
    
    def enter(self):
        """进入游戏场景"""
        self._init()

    def input(self, event):
        if self.is_replay:
            self._game_replay_input(event)
            return
        if self.is_game_paused:
            self.pause_panel.handle_event(event)
        if self.is_game_over:
            self.game_over_panel.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if self.is_game_paused or self.is_game_over:
                return

            if event.key == pygame.K_a:
                self.is_move_left = True
                if self.is_move_right:
                    self.is_move_right = False
            elif event.key == pygame.K_d:
                self.is_move_right = True
                if self.is_move_left:
                    self.is_move_left = False
            elif event.key == pygame.K_w:
                self.is_rotate = True
            elif event.key == pygame.K_s:
                # 加快下落速度
                self.move_down_timer.set_acceleration(GameConfig.MOVE_DOWN_INTERVAL / GameConfig.MOVE_DOWN_INTERVAL_ACCEL)
            elif event.key == pygame.K_SPACE:
                self.is_game_paused = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.is_move_left = False
            elif event.key == pygame.K_d:
                self.is_move_right = False
            elif event.key == pygame.K_w:
                self.is_rotate = False
            elif event.key == pygame.K_s:
                # 恢复正常下落速度
                self.move_down_timer.reset_acceleration()

    def update(self):
        if self.is_replay:
            if self.is_replay_over:
                return
            self._game_replay_update()
            return
        if self.is_game_over or self.is_game_paused:
            return
        
        # 更新定时器
        self.move_down_timer.update()
        if self.is_move_left:
            self.move_left_timer.update()
        if self.is_move_right:
            self.move_right_timer.update()
        if self.is_rotate:
            self.rotate_timer.update()
        self.auto_save_timer.update()

        # 更新帧计时器
        self.game_frame_counter.tick()
        
    def render(self):
        # 获取当前屏幕并渲染地图
        screen = pygame.display.get_surface()
        # 渲染游戏背景
        screen.blit(self.game_background, (0, 0))
        # 渲染地图纹理
        if self.map.texture:
            screen.blit(self.map.texture, (self.map_x, self.map_y))

        # 渲染当前方块
        if self.current_piece:
            block_texture = ResourcesManager().get_resource(ResId[self.current_piece.type.value], (GameConfig.TILE_SIZE, GameConfig.TILE_SIZE), alpha_val=200)
            for dx, dy in self.current_piece.get_block_positions():
                if self.map.is_valid_position(dx, dy):
                    screen.blit(block_texture, self.map_position_to_screen_position(dx, dy))

        # 渲染预测的下落位置
        if self.current_piece:
            block_texture = ResourcesManager().get_resource(ResId[self.current_piece.type.value], (GameConfig.TILE_SIZE, GameConfig.TILE_SIZE), alpha_val=50)
            predict_piece = PieceFactory().create_piece(self.current_piece.x, self.current_piece.y, self.current_piece.type, self.current_piece.rotation)
            is_down = True
            while is_down:
                predict_piece.move(0, 1)
                for x, y in predict_piece.get_block_positions():
                    tile = self.map.get_tile(x, y)
                    if tile and not tile.is_empty():
                        predict_piece.move(0, -1)  # 撤销移动
                        is_down = False
                        break
            for dx, dy in predict_piece.get_block_positions():
                if self.map.is_valid_position(dx, dy):
                    screen.blit(block_texture, self.map_position_to_screen_position(dx, dy))

        # 渲染方块预览
        if self.next_piece_queue:
            font = ResourcesManager().get_resource(ResId.FONT_STHUPO, 24)
            next_text = font.render("方块预览:", True, (235, 50, 35)) # 红色
            x, y = self.map_position_to_screen_position(self.next_piece_dx - 1, self.next_piece_dy - 2)
            screen.blit(next_text, (x - GameConfig.TILE_SIZE // 2, y - GameConfig.TILE_SIZE // 2))
            for i, next_piece in enumerate(self.next_piece_queue):
                block_texture = ResourcesManager().get_resource(ResId[next_piece.type.value], (GameConfig.TILE_SIZE, GameConfig.TILE_SIZE), alpha_val=230)
                for dx, dy in next_piece.get_block_positions():
                    dx, dy = dx - next_piece.x + self.next_piece_dx, dy - next_piece.y + self.next_piece_dy
                    x, y = self.map_position_to_screen_position(dx, dy + i * 5)
                    screen.blit(block_texture, (x + GameConfig.TILE_SIZE // 2, y + GameConfig.TILE_SIZE // 2))
        
        # 渲染分数
        font = ResourcesManager().get_resource(ResId.FONT_STHUPO, 24)
        score_text = font.render(f"分数: {self.score}", True, (235, 50, 35)) # 红色
        x, y = self.map_position_to_screen_position(self.score_dx, self.score_dy)
        screen.blit(score_text, (x - GameConfig.TILE_SIZE // 2, y - GameConfig.TILE_SIZE // 2))

        # 渲染游戏帧计数器
        font = ResourcesManager().get_resource(ResId.FONT_STHUPO, 24)
        game_frame_counter_text = font.render(f"游戏时间: {self.game_frame_counter.get_time_parts()}", True, (0, 0, 0)) # 黑色
        x, y = self.map_position_to_screen_position(self.game_frame_counter_dx, self.game_frame_counter_dy)
        screen.blit(game_frame_counter_text, (x - GameConfig.TILE_SIZE // 2, y - GameConfig.TILE_SIZE // 2))

        # 渲染游戏结束界面
        if self.is_game_over:
            self.game_over_panel.render()

        # 渲染暂停界面
        if self.is_game_paused:
            self.pause_panel.render()
        
        # 渲染重放暂停界面
        if self.is_replay_paused:
            self.replay_pause_panel.render()
        
        # 渲染重放结束界面
        if self.is_replay_over:
            self.replay_over_panel.render()

    def exit(self):
        # 停止定时器
        self.move_down_timer.stop()
        self.move_left_timer.stop()
        self.move_right_timer.stop()
        self.rotate_timer.stop()
        self.auto_save_timer.stop()

    def map_position_to_screen_position(self, map_x: int, map_y: int) -> Tuple[int, int]:
        """将地图坐标转换为屏幕坐标"""
        x, y = self.map.map_position_to_screen_position(map_x, map_y)
        return (self.map_x + x, self.map_y + y)
