import json

import pygame
from src.create.prefab_creator import create_bullet, create_cloud, create_enemy_spawner, create_input_player, create_player_square, create_square
from src.create.prefab_creator_interface import create_icon, create_space, create_text
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_player_lives import CPlayerLives
from src.ecs.components.c_player_score import CPlayerScore
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_special_charge import CSpecialCharge
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_cloud import CTagCloud
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
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bullet import system_screen_bullet
from src.ecs.systems.s_screen_player import system_screen_player
from src.ecs.systems.s_steering import system_steering
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class PlayScene(Scene):
    def __init__(self, game_engine, level:str):
        super().__init__(game_engine)
        with open("assets/cfg/window.json", encoding="utf-8") as window_file:
            self.window_cfg = json.load(window_file)
        with open("assets/cfg/enemies.json", encoding="utf-8") as enemies_file:
            self.enemies_cfg = json.load(enemies_file)
        with open("assets/cfg/level_01.json", encoding="utf-8") as level_01_file:
            self.level_cfg = json.load(level_01_file)
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
        self.num_killed_enemies = 0
        self.score = 0
        self.target_scene_over = "GAME_OVER"
        self.game_over = False
        
        full_sheet = ServiceLocator.images_service.get('assets/img/player.png')
        n_frames   = self.player_cfg["animations"]["number_frames"]
        fw         = full_sheet.get_width()  // n_frames
        fh         = full_sheet.get_height()

        self.life_icon = pygame.Surface((fw, fh), pygame.SRCALPHA)
        self.life_icon.blit(full_sheet, (0, 0), pygame.Rect(0, 0, fw, fh))

        scale_h = 28
        scale_w = int(fw * (scale_h / fh))
        self.life_icon = pygame.transform.scale(self.life_icon, (scale_w, scale_h))
        
    def do_create(self):
        self.game_over = False
        
        self.ecs_world.clear_database()

        self._player_entity = create_player_square(self.ecs_world, self.player_cfg, self.level_cfg["player_spawn"])
        self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
        self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
        self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)
        self._player_s_c = self.ecs_world.component_for_entity(self._player_entity, CSpecialCharge)
        self.ecs_world.add_component(self._player_entity, 
                                CPlayerLives(self.level_cfg["player_spawn"]["lives"]))
        self.ecs_world.add_component(self._player_entity,
                                     CPlayerScore())

        create_enemy_spawner(self.ecs_world, self.level_cfg)
        create_input_player(self.ecs_world)
        
        for cloud_event in self.level_cfg["cloud_spawn_events"]:
            pos = pygame.Vector2(cloud_event["position"]["x"], cloud_event["position"]["y"])
            vel = pygame.Vector2(0, 0) 
            create_cloud(self.ecs_world, pos, vel, cloud_event["cloud_type"], self.clouds_cfg)

    def do_update(self, delta_time:float, screen):
        if self.is_paused:
            return
        
        player_state = self.ecs_world.component_for_entity(self._player_entity, CPlayerState)
        
        if player_state.state == PlayerState.DEAD:
            self.game_over = True
            
        if self.game_over:
            self.in_transition = True
            self.elapsed_time = 0
            self.transition_duration = 3.0  # segundos antes de cambiar de escena
            # Reproducir sonido de game over si existe
            ServiceLocator.sounds_service.play('assets/snd/game_over.ogg')
            self.switch_scene(self.target_scene_over)  # Usamos la variable ya definida
            
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
                                      self.level_cfg, self.explosion_cfg)

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
    
    def do_draw(self, screen):
        screen.fill(self.game_engine.bg_color)
        
        # Vidas y Score
        score_count = 0
        lives_count = 0
        kills_count = 0
        if self.ecs_world.entity_exists(self._player_entity):
            c_score = self.ecs_world.component_for_entity(self._player_entity, CPlayerScore)
            c_lives = self.ecs_world.component_for_entity(self._player_entity, CPlayerLives)
            lives_count = c_lives.lives if c_lives else 0
            score_count = c_score.score if c_score else 0
            kills_count = c_score.kills if c_score else 0
        
        W, H = screen.get_size()
        white = pygame.Color(255, 255, 255)
        red = pygame.Color(255, 0, 0)
        cyan = pygame.Color(0, 174, 239)
        
        create_space(self.ecs_world, pygame.Vector2(W, 90), pygame.Vector2(0, 0), pygame.Color(0, 0, 0))
        create_space(self.ecs_world, pygame.Vector2(W, 50), pygame.Vector2(0, 470), pygame.Color(0, 0, 0))
       
        create_text(self.ecs_world, "1-UP", 14, white, pygame.Vector2( 50,  15), "left")
        create_text(self.ecs_world, "HI-SCORE", 14, red,   pygame.Vector2(250,  15), "center")
        create_text(self.ecs_world, "2-UP", 14, white, pygame.Vector2(400,  15), "left")

        create_text(self.ecs_world, str(score_count), 14, white, pygame.Vector2(62, 40), "left")
        create_text(self.ecs_world, "00", 14, white, pygame.Vector2(250, 40), "center")
        create_text(self.ecs_world, "CREDIT  00", 14, cyan,  pygame.Vector2(470, 480), "right")
        create_text(self.ecs_world, f"KILLS  {kills_count}", 14, cyan,  pygame.Vector2(50, 480), "left")
        
        icon_y = 58
        icon_x0 = 20
        gap = 30
        
        for i in range(lives_count):
            create_icon(self.ecs_world,
                        self.life_icon,
                        pygame.Vector2(icon_x0 + i * gap, icon_y))
        
        if self.is_paused:
            render_queue = []
            for ent, (c_t, c_s) in self.ecs_world.get_components(CTransform, CSurface):
                # Solo dibujar entidades que tengan el tag de nube
                if self.ecs_world.has_component(ent, CTagCloud):
                    size = self.ecs_world.component_for_entity(ent, CTagCloud).get_size()
                    layer = {"small": 0, "medium": 1, "large": 3}.get(size, 2)
                    render_queue.append((layer, c_s.surf, c_t.pos, c_s.area))

            render_queue.sort(key=lambda item: item[0])
            for _, surf, pos, area in render_queue:
                screen.blit(surf, pos, area=area)
            
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            font = ServiceLocator.fonts_service.get('assets/fnt/PressStart2P.ttf', 24)
            pause_text, text_rect = font.render("PAUSED", pygame.Color(255, 255, 255))
            text_rect.center = (screen.get_width()//2, screen.get_height()//2 -20)
            screen.blit(pause_text, text_rect)
            
            font_small = ServiceLocator.fonts_service.get('assets/fnt/PressStart2P.ttf', 16)
            instructions, instr_rect = font_small.render("Press P to resume", pygame.Color(255, 255, 255))
            instr_rect.center = (screen.get_width()//2, screen.get_height()//2 + 20)
            screen.blit(instructions, instr_rect)
        else:
            system_rendering(self.ecs_world, screen)
        
        pygame.display.flip()