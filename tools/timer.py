import pygame
from typing import Callable, Optional


class Timer:
    """
    基于pygame的定时器类，提供暂停、加速、触发回调等功能
    """
    
    def __init__(self, interval: int, callback: Optional[Callable] = None, repeat: bool = True):
        """
        初始化定时器
        
        Args:
            interval: 定时间隔（毫秒）
            callback: 定时器触发时的回调函数
            repeat: 是否重复触发，False则只触发一次
        """
        self.interval = interval  # 原始间隔时间（毫秒）
        self.callback = callback  # 回调函数
        self.repeat = repeat  # 是否重复
        
        # 定时器状态 - True表示运行，False表示暂停
        self.state = False
        
        # 时间相关
        self.last_time = 0  # 上次触发时间
        self.accumulated_time = 0  # 累积时间
        
        # 加速相关 - 实时计算，不存储加速间隔
        self.acceleration_factor = 1.0  # 加速因子
        
    @property
    def is_running(self) -> bool:
        """检查定时器是否正在运行"""
        return self.state is True
        
    @property
    def is_stop(self) -> bool:
        """检查定时器是否已暂停"""
        return self.state is False
        
    @property
    def current_interval(self) -> int:
        """获取当前间隔时间（实时计算）"""
        return int(self.interval / self.acceleration_factor)
        
    def start(self):
        """启动定时器"""
        self.state = True
        self.last_time = pygame.time.get_ticks()
        self.accumulated_time = 0
        
    def stop(self):
        """停止定时器"""
        self.state = False

    def set_acceleration(self, factor: float):
        """
        设置加速因子
        
        Args:
            factor: 加速因子，大于1表示加速，小于1表示减速
        """
        self.acceleration_factor = factor
            
    def reset_acceleration(self):
        """重置加速，恢复正常速度"""
        self.acceleration_factor = 1.0
            
    def set_interval(self, interval: int):
        """设置新的定时间隔"""
        self.interval = interval
            
    def update(self):
        """更新定时器状态，检查是否需要触发回调"""
        if self.state is False:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_time
        
        # 检查是否达到触发时间
        if elapsed_time >= self.current_interval:
            # 触发回调
            if self.callback:
                try:
                    self.callback()
                except Exception as e:
                    print(f"定时器回调函数执行错误: {e}")
            
            # 重置计时器
            self.last_time = current_time
            
            # 如果不重复，则停止定时器
            if not self.repeat:
                self.stop()
        
    def reset(self):
        """重置定时器到初始状态"""
        self.state = None
        self.last_time = 0
        self.accumulated_time = 0
        self.acceleration_factor = 1.0