import math
import pygame
from src.create.prefab_creator_interface import create_text
from src.ecs.components.c_input_command import CInputCommand
from src.engine.scenes.scene import Scene
from src.engine.service_locator import ServiceLocator


class GameOverScene(Scene):
    def do_create(self):
        self.in_transition = False
        self.transition_duration = 1.5
        self.elapsed_time = 0
        self.target_scene = "MENU_SCENE"
        
        white = pygame.Color(255, 255, 255)
        red = pygame.Color(255, 0, 0)
        cyan = pygame.Color(0, 174, 239)
        yell = pygame.Color(255, 212, 63)

        create_text(self.ecs_world, "GAME OVER", 35, red, pygame.Vector2(250, 230), "center")
        create_text(self.ecs_world, "Press ESC for Main Menu", 14, cyan,   pygame.Vector2(250,  290), "center")
        
        start_ent = self.ecs_world.create_entity()
        self.ecs_world.add_component(start_ent,
                                     CInputCommand("MENU_SCENE", pygame.K_ESCAPE))
        
    def do_update(self, dt, screen):
        if self.in_transition:
            self.elapsed_time += dt
            if self.elapsed_time >= self.transition_duration:
                self.switch_scene(self.target_scene)
        
        super().do_update(dt, screen)
    
    def do_action(self, action: CInputCommand):
        if action.name == "MENU_SCENE":
            ServiceLocator.sounds_service.play('assets/snd/game_paused.ogg')
            self.in_transition = True
            
    def do_draw(self, screen):
        screen.fill(pygame.Color(0, 96, 105))
        super().do_draw(screen)
        if self.in_transition:
            self._draw_clock_animation(screen)
    
    def _draw_clock_animation(self, screen: pygame.Surface):
        progress = min(1.0, self.elapsed_time / self.transition_duration)
        sweep_angle = 360.0 * progress
        start_angle = -90
        sector_size = 360 / 36
        max_radius = math.hypot(screen.get_width(), screen.get_height())

        turquoise = pygame.Color(0, 0, 0)
        tile = 18
        cx, cy = screen.get_width() // 2, screen.get_height() // 2

        sectors_to_draw = int(sweep_angle // sector_size) + 1

        for i in range(sectors_to_draw):
            ang_start = start_angle - i       * sector_size
            ang_end   = start_angle - (i + 1) * sector_size
            
            if - (ang_end - start_angle) > sweep_angle:
                ang_end = start_angle - sweep_angle

            points = [(cx, cy)]
            steps  = 6
            for j in range(steps + 1):
                t = j / steps
                ang = math.radians(ang_start + t * (ang_end - ang_start))
                x   = cx + math.cos(ang) * max_radius
                y   = cy + math.sin(ang) * max_radius
                points.append((x, y))
            pygame.draw.polygon(screen, turquoise, points)

            rad_start = math.radians(ang_start)
            rad_end   = math.radians(ang_end)
            for r in range(0, int(max_radius), tile):
                x0 = cx + math.cos(rad_start) * r
                y0 = cy + math.sin(rad_start) * r
                x1 = cx + math.cos(rad_end)   * r
                y1 = cy + math.sin(rad_end)   * r
                dist   = math.hypot(x1 - x0, y1 - y0)
                steps  = max(1, int(dist // tile))
                for k in range(steps + 1):
                    t  = k / steps
                    xq = int(x0 + t * (x1 - x0) - tile // 2)
                    yq = int(y0 + t * (y1 - y0) - tile // 2)
                    screen.fill(turquoise,
                                pygame.Rect(xq, yq, tile, tile))