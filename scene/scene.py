import pygame


# 场景类
class Scene:
    def __init__(self, name):
        self.name = name

    def enter(self):
        pass

    def input(self, event):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def exit(self):
        pass