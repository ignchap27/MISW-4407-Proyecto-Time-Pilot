import esper
import pygame

from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_rendering import system_rendering


class Scene:
    def __init__(self, game_engine):
        self.ecs_world = esper.World()
        self.game_engine = game_engine
        self.screen_rect = self.game_engine.screen.get_rect()
        
    def create(self) -> None:
        """Se llama al entrar en la escena. Aquí creas entidades, sistemas, etc."""
        self.do_create()

    def process_events(self, event) -> None:
        system_input_player(self.ecs_world, event, self.do_action)

    def simulate(self, dt: float, screen) -> None:
        self.do_update(dt, screen)
        self.ecs_world._clear_dead_entities()
        
    def draw(self, screen) -> None:
        self.do_draw(screen)

    def clean(self) -> None:
        self.ecs_world.clear_database()
        self.do_clean()
        
    def switch_scene(self, new_scene_name:str):
        self.game_engine.switch_scene(new_scene_name)

    def do_create(self):
        pass
    
    def do_process_events(self):
        pass
    
    def do_update(self, dt: float, screen):
        pass
    
    def do_draw(self, screen):
        system_rendering(self.ecs_world, screen)
    
    def do_clean(self):
        pass
    
    def do_action(self, c_input):
        pass