import pygame
import math
from src.create.prefab_creator_interface import create_text
from src.ecs.components.c_input_command import CInputCommand
from src.engine.scenes.scene import Scene
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.engine.service_locator import ServiceLocator


class MenuScene(Scene):
    
    def do_create(self):
        self.in_transition = False
        self.transition_duration = 1.5
        self.elapsed_time = 0
        self.target_scene = "LEVEL_01"

        white = pygame.Color(255, 255, 255)
        red = pygame.Color(255, 0, 0)
        cyan = pygame.Color(0, 174, 239)
        yell = pygame.Color(255, 212, 63)

        logo = ServiceLocator.images_service.get("assets/img/game_logo.png")
        logo = pygame.transform.scale(logo, (300, 80))
        logo_ent = self.ecs_world.create_entity()
        self.ecs_world.add_component(logo_ent, CTransform(pygame.Vector2(100, 150)))
        self.ecs_world.add_component(logo_ent, CSurface.from_surface(logo))

        create_text(self.ecs_world, "1-UP",     14, white, pygame.Vector2( 50,  15), "left")
        create_text(self.ecs_world, "HI-SCORE", 14, red,   pygame.Vector2(250,  15), "center")
        create_text(self.ecs_world, "2-UP",     14, white, pygame.Vector2(400,  15), "left")

        create_text(self.ecs_world, "00",   14, white, pygame.Vector2( 62,  33), "left")
        create_text(self.ecs_world, "00", 14, white, pygame.Vector2(250,  33), "center")
        create_text(self.ecs_world, "00",   14, white, pygame.Vector2(412,  33), "left")

        create_text(self.ecs_world, "PLAY",                 22, cyan, pygame.Vector2(250, 110), "center")
        create_text(self.ecs_world, "PLEASE  PUSH  ENTER",  18, cyan, pygame.Vector2(250, 260), "center")
        create_text(self.ecs_world, "ARROWS TO MOVE", 18, yell,  pygame.Vector2(250, 300), "center")
        create_text(self.ecs_world, "MOUSE TO SHOOT", 18, yell,  pygame.Vector2(250, 340), "center")
        create_text(self.ecs_world, "P TO PAUSE", 18, yell,  pygame.Vector2(250, 380), "center")

        create_text(self.ecs_world, "©  UNIANDES  2025", 14, white, pygame.Vector2(250, 455), "center")
        create_text(self.ecs_world, "CREDIT  00",        14, cyan,  pygame.Vector2(470, 480), "right")

        start_ent = self.ecs_world.create_entity()
        self.ecs_world.add_component(start_ent,
                                     CInputCommand("START_GAME", pygame.K_RETURN))
    
    def do_update(self, dt, screen):
        if self.in_transition:
            self.elapsed_time += dt
            if self.elapsed_time >= self.transition_duration:
                self.switch_scene(self.target_scene)
        
        super().do_update(dt, screen)
        
    def do_action(self, action: CInputCommand):
        if action.name == "START_GAME" and not self.in_transition:
            ServiceLocator.sounds_service.play('assets/snd/game_start.ogg')
            self.in_transition = True
            self.elapsed_time = 0
            
    def do_draw(self, screen):
        screen.fill(pygame.Color(0, 0, 0))
        super().do_draw(screen)
        if self.in_transition:
            self._draw_clock_animation(screen)
    
    def _draw_clock_animation(self, screen: pygame.Surface):
        progress = min(1.0, self.elapsed_time / self.transition_duration)
        sweep_angle = 360.0 * progress
        start_angle = -90
        sector_size = 360 / 36
        max_radius = math.hypot(screen.get_width(), screen.get_height())

        turquoise = pygame.Color(0, 96, 105)
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