import json

import pygame
from src.create.prefab_creator import create_bullet, create_cloud, create_enemy_spawner, create_input_player, create_player_square
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_special_charge import CSpecialCharge
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_cloud_behavior import system_cloud_behavior
from src.ecs.systems.s_collision_enemy_bullet import system_collision_enemy_bullet
from src.ecs.systems.s_collision_enemy_fireball import system_collision_enemy_fireball
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_enemy_state import system_enemy_state
from src.ecs.systems.s_explosion_kill import system_explosion_kill
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_object_movement import system_object_movement
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_screen_bullet import system_screen_bullet
from src.ecs.systems.s_screen_player import system_screen_player
from src.ecs.systems.s_steering import system_steering
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class PlayScene(Scene):
    def __init__(self, game_engine):
        super().__init__(game_engine)
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
        with open("assets/cfg/clouds.json", encoding="utf-8") as clouds_file:
            self.clouds_cfg = json.load(clouds_file)
        with open("assets/cfg/interface.json", "r") as file:
            self.interface_config = json.load(file)
            
        self.is_paused = False
        
    def do_create(self):
        self._player_entity = create_player_square(self.ecs_world, self.player_cfg, self.level_01_cfg["player_spawn"])
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
        self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)
        self._player_s_c = self.ecs_world.component_for_entity(self._player_entity, CSpecialCharge)

        create_enemy_spawner(self.ecs_world, self.level_01_cfg)
        create_input_player(self.ecs_world)
        
        for cloud_event in self.level_01_cfg["cloud_spawn_events"]:
            pos = pygame.Vector2(cloud_event["position"]["x"], cloud_event["position"]["y"])
            vel = pygame.Vector2(0, 0) 
            create_cloud(self.ecs_world, pos, vel, cloud_event["cloud_type"], self.clouds_cfg)
            
    def do_update(self, delta_time:float, screen):
        if self.is_paused:
            return
        
        system_enemy_spawner(self.ecs_world, self.enemies_cfg,delta_time)
        system_movement(self.ecs_world, delta_time, self._player_entity)
        system_object_movement(self.ecs_world, delta_time, self._player_entity)

        system_screen_player(self.ecs_world, screen)
        system_screen_bullet(self.ecs_world, screen)
        system_cloud_behavior(self.ecs_world, screen)


        system_collision_enemy_bullet(self.ecs_world, self._player_s_c, self.explosion_cfg)
        system_collision_enemy_fireball(self.ecs_world, self._player_s_c, self.explosion_cfg)
        system_collision_player_enemy(self.ecs_world, self._player_entity,
                                      self.level_01_cfg, self.explosion_cfg)

        system_explosion_kill(self.ecs_world)
        system_steering(self.ecs_world, delta_time, self._player_entity)

        system_player_state(self.ecs_world, self.player_cfg)
        system_enemy_state(self.ecs_world)

        system_animation(self.ecs_world, delta_time)

        self.ecs_world._clear_dead_entities()
        self.num_bullets = len(self.ecs_world.get_component(CTagBullet))
        
    def do_action(self, c_input: CInputCommand):
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
        if c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]

        if c_input.name == "PLAYER_FIRE":
            create_bullet(self.ecs_world, c_input.mouse_pos, self._player_c_t.pos,
                          self._player_c_s.area.size, self.bullet_cfg)
            
    def process_events(self, event):
        # Manejar pausa (tecla P)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self.is_paused = not self.is_paused
            ServiceLocator.sounds_service.play('assets/snd/game_paused.ogg')
        if not self.is_paused:
            super().process_events(event)
    