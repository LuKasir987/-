import pygame
from resources.resource_manager import ResId, ResourcesManager
from ui.button import Button, ButtonState

class Panel:
    def __init__(self, x: int, y: int, width: int, height: int, padding: int = 100, spacing: int = 100, font_size: int = 36, res_id: ResId = ResId.PANEL):
        """
        初始化面板
        
        Args:
            x (int): 面板X坐标
            y (int): 面板Y坐标
            width (int): 面板宽度
            height (int): 面板高度
            padding (int): 水平间距
            spacing (int): 垂直间距
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = padding
        self.spacing = spacing
        self.font_size = font_size
        
        self.image = ResourcesManager().get_resource(res_id, (self.width, self.height)) if res_id else None
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttons: list[Button] = []

    def set_padding(self, padding: int):
        """设置水平间距"""
        self.padding = padding
        self._update_button_positions()

    def set_spacing(self, spacing: int):
        """设置垂直间距"""
        self.spacing = spacing
        self._update_button_positions()

    def add_button(self, text: str, callback=None):
        """
        添加按钮
        
        Args:
            text (str): 按钮文本
            callback (function): 按钮点击回调函数
        """
        button = Button(0, 0, 0, 0, text=text, callback=callback)
        button.set_background_image(ButtonState.IDLE, ResId.BUTTON_IDLE)
        button.set_background_image(ButtonState.HOVERED, ResId.BUTTON_HOVERED)
        button.set_background_image(ButtonState.PRESSED, ResId.BUTTON_PRESSED)

        self.buttons.append(button)
        self._update_button_rect()

    def _update_button_rect(self):
        """更新所有按钮的位置（垂直居中对齐）"""
        if not self.buttons:
            return
            
        # 使所有按钮在面板中垂直居中
        start_y = self.y + self.spacing
        button_width = self.width - 2 * self.padding
        button_height = (self.height - (len(self.buttons) + 1) * self.spacing) // (len(self.buttons))
        # 水平居中
        x = self.x + (self.width - button_width) // 2

        for i, button in enumerate(self.buttons):
            # 按钮宽度为面板宽度减去两侧水平间距
            button.rect.width = button_width
            # 按钮高度根据面板高度和按钮数量计算
            button.rect.height = button_height
            # 垂直排列
            y = start_y + i * (button.rect.height + self.spacing)
            button.rect.topleft = (x, y)

    def handle_event(self, event):
        """处理事件，传递给所有按钮"""
        for button in self.buttons:
            button.handle_event(event)

    def render(self):
        """渲染面板和所有按钮"""
        screen = pygame.display.get_surface()
        # 绘制面板背景
        if self.image:
            screen.blit(self.image, self.rect)
        
        # 渲染所有按钮
        for button in self.buttons:
            button.render()
