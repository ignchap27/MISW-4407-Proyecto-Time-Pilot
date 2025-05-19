import asyncio
import json
import pygame
import esper
import math

from src.ecs.systems.s_animation import system_animation

from src.ecs.systems.s_collision_enemy_fireball import system_collision_enemy_fireball
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_collision_enemy_bullet import system_collision_enemy_bullet

from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_enemy_state import system_enemy_state
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.systems.s_screen_player import system_screen_player
from src.ecs.systems.s_screen_bullet import system_screen_bullet

from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_explosion_kill import system_explosion_kill

from src.ecs.components.c_special_charge import CSpecialCharge
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_bullet import CTagBullet

from src.ecs.components.c_input_command import CInputCommand, CommandPhase

from src.create.prefab_creator import create_enemy_spawner, create_fireball, create_input_player, create_player_square, create_bullet
from src.engine.service_locator import ServiceLocator


class GameEngine:
    def __init__(self) -> None:
        self._load_config_files()

        pygame.init()
        pygame.display.set_caption(self.window_cfg["title"])
        print("Window size:", self.window_cfg["size"])

        self.screen = pygame.display.set_mode((self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]), 0)

        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = self.window_cfg["framerate"]
        self.delta_time = 0
        self.bg_color = pygame.Color(self.window_cfg["bg_color"]["r"],
                                     self.window_cfg["bg_color"]["g"],
                                     self.window_cfg["bg_color"]["b"])
        self.ecs_world = esper.World()

        self.num_bullets = 0

        font_path = "assets/fnt/PressStart2P.ttf"
        text_title_size = 40
        text_size = 20

        self.title_font = ServiceLocator.fonts_service.get(font_path, text_title_size)
        self.font = ServiceLocator.fonts_service.get(font_path, text_size)
        self.text_title = "Time Pilot"
        self.text_subtitle = "Please deposit coin"
        
        color_data = self.interface_config["title_text_color"]
        self.text_title_color = (color_data["r"], color_data["g"], color_data["b"])

        color_data = self.interface_config["normal_text_color"]
        self.text_subtitle_color = (color_data["r"], color_data["g"], color_data["b"])

        self.is_paused = False

        self._player_angle = 0.0
        self._player_scroll_speed = self.player_cfg["input_velocity"]
        self._player_is_thrusting = False

        try:
            with open("assets/cfg/fireball.json", encoding="utf-8") as fireball_file:
                self.fireball_cfg = json.load(fireball_file)
        except FileNotFoundError:
            print("Warning: assets/cfg/fireball.json not found. Special attack might not work.")
            self.fireball_cfg = None

    def _load_config_files(self):
        with open("assets/cfg/window.json", encoding="utf-8") as window_file:
            self.window_cfg = json.load(window_file)
        with open("assets/cfg/enemies.json", encoding="utf-8") as enemies_file:
            self.enemies_cfg = json.load(enemies_file)
        with open("assets/cfg/level_01.json", encoding="utf-8") as level_01_file:
            self.level_01_cfg = json.load(level_01_file)
        with open("assets/cfg/player.json", encoding="utf-8") as player_file:
            self.player_cfg = json.load(player_file)
        with open("assets/cfg/bullet.json", encoding="utf-8") as bullet_file:
            self.bullet_cfg = json.load(bullet_file)
        with open("assets/cfg/explosion.json", encoding="utf-8") as explosion_file:
            self.explosion_cfg = json.load(explosion_file)
        with open("assets/cfg/interface.json", "r") as file:
            self.interface_config = json.load(file)

    async def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)
        self._clean()

    def _create(self):
        player_spawn_pos_cfg = {
            "position": {
                "x": self.screen.get_width() / 2,
                "y": self.screen.get_height() / 2
            }
        }
        self._player_entity = create_player_square(self.ecs_world, self.player_cfg, player_spawn_pos_cfg)
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
        self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)
        self._player_s_c = self.ecs_world.component_for_entity(self._player_entity, CSpecialCharge)
        
        if self._player_c_v:
            self._player_c_v.vel = pygame.Vector2(0, 0)

        create_enemy_spawner(self.ecs_world, self.level_01_cfg)
        create_input_player(self.ecs_world)

    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.is_paused = not self.is_paused
            if not self.is_paused:
                system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        if self.is_paused:
            return
        
        player_screen_center_x = self.screen.get_width() / 2
        player_screen_center_y = self.screen.get_height() / 2
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        delta_x = mouse_x - player_screen_center_x
        delta_y = mouse_y - player_screen_center_y

        direction_to_mouse = pygame.Vector2(delta_x, delta_y)
        if direction_to_mouse.length_squared() > 0:
            self._player_angle = pygame.Vector2(0, -1).angle_to(direction_to_mouse)

        self._player_angle %= 360
        if self._player_angle < 0:
            self._player_angle += 360

        system_enemy_spawner(self.ecs_world, self.enemies_cfg, self.delta_time)
        
        current_scroll_magnitude = self._player_scroll_speed if self._player_is_thrusting else 0
        player_direction_vector = pygame.Vector2(0, -1).rotate(self._player_angle)
        scroll_vector = -player_direction_vector * current_scroll_magnitude
        
        system_movement(self.ecs_world, self.delta_time, scroll_vector)

        system_screen_bounce(self.ecs_world, self.screen)
        system_screen_player(self.ecs_world, self.screen)
        system_screen_bullet(self.ecs_world, self.screen)

        system_collision_enemy_bullet(self.ecs_world, self._player_s_c, self.explosion_cfg)
        system_collision_enemy_fireball(self.ecs_world, self._player_s_c, self.explosion_cfg)
        system_collision_player_enemy(self.ecs_world, self._player_entity,
                                      self.level_01_cfg, self.explosion_cfg)

        system_explosion_kill(self.ecs_world)

        system_player_state(self.ecs_world, self.player_cfg,  self._player_angle, self._player_is_thrusting)
        system_enemy_state(self.ecs_world)

        system_animation(self.ecs_world, self.delta_time)

        self.ecs_world._clear_dead_entities()
        self.num_bullets = len(self.ecs_world.get_component(CTagBullet))

    def _draw(self):
        self.screen.fill(self.bg_color)
        if self.is_paused:
            text_rect = self.title_font.get_rect("Paused Game")

            x = (self.screen.get_width() - text_rect.width) // 2
            y = (self.screen.get_height() - text_rect.height) // 2

            self.title_font.render_to(self.screen, (x, y), "Paused Game", (255, 0, 0))
        else:
            self.title_font.render_to(self.screen, (10, 10), self.text_title, self.text_title_color)
            self.font.render_to(self.screen, (10, 50), self.text_subtitle, self.text_subtitle_color)

            charge_text = f"Special Charge: {self._player_s_c.get_charge()}"
            self.font.render_to(self.screen, (10, 90), charge_text, (0, 255, 0))

            system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()
        
    def _do_action(self, c_input: CInputCommand):
        if c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self._player_is_thrusting = True
            elif c_input.phase == CommandPhase.END:
                self._player_is_thrusting = False
        if c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self._player_is_thrusting = False

        if c_input.name == "PLAYER_FIRE" and self.num_bullets < self.level_01_cfg["player_spawn"]["max_bullets"]:
            ServiceLocator.sounds_service.play(self.bullet_cfg["sound"])
            player_screen_center_pos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
            
            create_bullet(self.ecs_world, 
                          player_screen_center_pos,
                          self._player_c_s.area.size,
                          self._player_angle,
                          self.bullet_cfg)
        
        if c_input.name == "SPECIAL_ATTACK" and self._player_s_c.is_fully_charged():
            if self.fireball_cfg:
                player_center_pos = self._player_c_t.pos + pygame.Vector2(self._player_c_s.area.width / 2, self._player_c_s.area.height / 2)
            else:
                print("Warning: Fireball config not loaded, special attack cannot be performed.")
