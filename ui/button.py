import pygame
from enum import Enum
import sys
import os
from resources.resource_manager import ResourcesManager, ResId

class ButtonState(Enum):
    """按钮状态枚举"""
    IDLE = 1
    HOVERED = 2
    PRESSED = 3

class Button:
    """自定义按钮类，支持三种状态和回调事件"""
    
    def __init__(self, x, y, width, height, text="", font_size=24, callback=None):
        """
        初始化按钮
        
        Args:
            x (int): 按钮X坐标
            y (int): 按钮Y坐标
            width (int): 按钮宽度
            height (int): 按钮高度
            text (str): 按钮文本
            font_size (int): 字体大小
            callback (function): 点击回调函数
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.callback = callback
        self.state = ButtonState.IDLE
        
        # 创建字体对象
        try:
            self.font = ResourcesManager().get_resource(ResId.FONT_STHUPO)
        except Exception as e:
            print(f"字体加载失败: {e}")
            self.font = pygame.font.Font(None, font_size)
        
        # 默认颜色配置
        self.colors = {
            ButtonState.IDLE: {
                'bg': (200, 200, 200),
                'border': (100, 100, 100),
                'text': (0, 0, 0)
            },
            ButtonState.HOVERED: {
                'bg': (180, 180, 180),
                'border': (80, 80, 80),
                'text': (235, 50, 35) # 红色
            },
            ButtonState.PRESSED: {
                'bg': (160, 160, 160),
                'border': (60, 60, 60),
                'text': (235, 50, 35) # 红色
            }
        }
        
        # 背景图片（可选）
        self.background_images = {
            ButtonState.IDLE: None,
            ButtonState.HOVERED: None,
            ButtonState.PRESSED: None
        }
        
        # 是否被按下
        self.is_pressed = False
    
    def set_colors(self, state, bg_color=None, border_color=None, text_color=None):
        """
        设置特定状态的颜色
        
        Args:
            state (ButtonState): 按钮状态
            bg_color (tuple): 背景颜色 (R, G, B)
            border_color (tuple): 边框颜色 (R, G, B)
            text_color (tuple): 文本颜色 (R, G, B)
        """
        if bg_color is not None:
            self.colors[state]['bg'] = bg_color
        if border_color is not None:
            self.colors[state]['border'] = border_color
        if text_color is not None:
            self.colors[state]['text'] = text_color
    
    def set_background_image(self, state: ButtonState, res_id: ResId):
        """
        设置特定状态的背景图片（使用资源管理器）
        
        Args:
            state (ButtonState): 按钮状态
            res_id (ResId): 资源ID
        """
        
        # 根据ResId确定对应的图片
        if res_id:
            self.background_images[state] = res_id
        else:
            print(f"未知的资源ID: {res_id}")
            self.background_images[state] = None
    
    def set_position(self, x, y):
        """设置按钮位置"""
        self.rect.x = x
        self.rect.y = y
    
    def set_text(self, text):
        """设置按钮文本"""
        self.text = text
    
    def set_callback(self, callback):
        """设置回调函数"""
        self.callback = callback
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if self.state != ButtonState.PRESSED:
                    self.state = ButtonState.HOVERED
            else:
                self.state = ButtonState.IDLE
                self.is_pressed = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.state = ButtonState.PRESSED
                self.is_pressed = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_pressed:
                self.is_pressed = False
                if self.rect.collidepoint(event.pos):
                    self.state = ButtonState.HOVERED
                    if self.callback:
                        self.callback()
                    return True
                else:
                    self.state = ButtonState.IDLE
        
        return False
    
    def render(self):
        """
        绘制按钮
        
        Args:
            surface: pygame表面
        """
        # 获取当前状态的颜色
        colors = self.colors[self.state]
        
        # 绘制背景或背景图片
        screen = pygame.display.get_surface()
        if self.background_images[self.state]:
            # 加载背景图片
            image = ResourcesManager().get_resource(self.background_images[self.state], (self.rect.width, self.rect.height))
            screen.blit(image, self.rect)
        else:
            pygame.draw.rect(screen, colors['bg'], self.rect)
            # 绘制边框
            pygame.draw.rect(screen, colors['border'], self.rect, 2)
        
        
        # 绘制文本
        if self.text:
            text_surface = self.font.render(self.text, True, colors['text'])
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
