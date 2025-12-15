from scene.scene import Scene
from core.singleton import Singleton


class SceneManager(Singleton):
    scenes: dict[str, Scene] = {}
    active_scene: Scene = None
    
    def exist_scene(self, name) -> bool:
        return name in self.scenes
    
    def add_scene(self, scene: Scene):
        if self.exist_scene(scene.name):
            raise ValueError(f"Scene {scene.name} already exists")
        self.scenes[scene.name] = scene
    
    def remove_scene(self, name):
        if not self.exist_scene(name):
            raise ValueError(f"Scene {name} does not exist")
        del self.scenes[name]

    def get_scene(self, name):
        return self.scenes[name]
    
    def set_active_scene(self, scene_name: str):
        """设置当前活动场景 删除旧场景"""
        if not self.exist_scene(scene_name):
            raise ValueError(f"Scene {scene_name} does not exist")
        
        if self.active_scene:
            self.active_scene.exit()
            self.remove_scene(self.active_scene.name)

        self.active_scene = self.scenes[scene_name]
        self.active_scene.enter()
    
    def input(self, event):
        self.active_scene.input(event)
    
    def update(self):
        self.active_scene.update()

    def render(self):
        self.active_scene.render()
