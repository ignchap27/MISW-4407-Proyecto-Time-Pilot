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
        # Estado de transición
        self.in_transition = False
        self.transition_duration = 1.5  # duración en segundos
        self.elapsed_time = 0
        self.target_scene = "LEVEL_01"
        
        # Cargar el logo del juego
        logo_surface = pygame.image.load("assets/img/game_logo.png").convert_alpha()
        # Ajustar tamaño si es necesario
        logo_surface = pygame.transform.scale(logo_surface, (400, 150))
                
        # Crear entidad para el logo
        logo_entity = self.ecs_world.create_entity()
        
        # Calcular la posición centrada (compensando con el tamaño del logo)
        logo_x = (self.screen_rect.width - logo_surface.get_width()) // 2
        logo_y = 80  # Posición vertical fija
        
        # Usar la esquina superior izquierda como punto de referencia
        logo_pos = pygame.Vector2(logo_x, logo_y)
        self.ecs_world.add_component(logo_entity, CTransform(logo_pos))
        self.ecs_world.add_component(logo_entity, CSurface.from_surface(logo_surface))
        
        # Textos del menú
        create_text(self.ecs_world, "- PRESS Z TO START -", 20,
                    pygame.Color(255, 255, 255), pygame.Vector2(250, 300), 'center')
        
        create_text(self.ecs_world, "- ARROW TO MOVE -", 16,
                    pygame.Color(255, 255, 255), pygame.Vector2(250, 350), 'center')
        
        create_text(self.ecs_world, "- MOUSE TO SHOOT -", 16,
                    pygame.Color(255, 255, 255), pygame.Vector2(250, 400), 'center')
        
        create_text(self.ecs_world, "- P TO PAUSE -", 16,
                    pygame.Color(255, 255, 255), pygame.Vector2(250, 450), 'center')
        
        start_game_action = self.ecs_world.create_entity()
        self.ecs_world.add_component(start_game_action,
                                     CInputCommand("START_GAME", pygame.K_z))
    
    def do_update(self, dt, screen):
        # Si estamos en transición, actualizar el temporizador
        if self.in_transition:
            self.elapsed_time += dt
            if self.elapsed_time >= self.transition_duration:
                # La animación terminó, cambiamos a la siguiente escena
                self.switch_scene(self.target_scene)
        
        # Llamar a la implementación base para actualizar sistemas ECS
        super().do_update(dt, screen)
        
    def do_action(self, action: CInputCommand):
        if action.name == "START_GAME" and not self.in_transition:
            ServiceLocator.sounds_service.play('assets/snd/game_start.ogg')
            # Iniciar la animación de transición
            self.in_transition = True
            self.elapsed_time = 0
            
    def do_draw(self, screen):
        # Establecer fondo negro
        screen.fill(pygame.Color(0, 0, 0))
        
        if not self.in_transition:
            # Dibujo normal del menú usando el sistema de renderizado
            super().do_draw(screen)
        else:
            # Dibujar la animación del reloj
            self._draw_clock_animation(screen)
    
    def _draw_clock_animation(self, screen):
        # Calcular el progreso (0.0 a 1.0)
        progress = min(1.0, self.elapsed_time / self.transition_duration)
        
        # Dimensiones de la pantalla
        width, height = screen.get_width(), screen.get_height()
        
        # Color turquesa/cian típico de Time Pilot
        turquoise_color = pygame.Color(0, 96, 105)
        
        # Centro de la pantalla
        center_x, center_y = width // 2, height // 2
        
        # Radio máximo para cubrir toda la pantalla
        max_radius = int(math.sqrt(width**2 + height**2) / 2) + 50
        
        # Cuántos sectores dibujar (más = más suave)
        num_sectors = 36  # Cada 10 grados
        
        # Ángulo de barrido basado en el progreso (0 a 360 grados)
        sweep_angle = 360.0 * progress
        
        # Dibujar sectores circulares para crear el efecto de barrido
        for i in range(num_sectors):
            sector_start_angle = i * (360 / num_sectors)
            sector_end_angle = (i + 1) * (360 / num_sectors)
            
            # Solo dibujar sectores dentro del ángulo de barrido actual
            if sector_start_angle <= sweep_angle:
                # Calcular puntos para un sector
                points = [
                    (center_x, center_y)  # Centro
                ]
                
                # Cantidad de puntos en el arco exterior
                arc_points = 8
                
                # Añadir puntos en el arco exterior
                for j in range(arc_points + 1):
                    arc_angle = sector_start_angle + j * (sector_end_angle - sector_start_angle) / arc_points
                    arc_angle_rad = math.radians(arc_angle)
                    x = center_x + math.cos(arc_angle_rad) * max_radius
                    y = center_y + math.sin(arc_angle_rad) * max_radius
                    points.append((x, y))
                
                # Crear un polígono para el sector
                pygame.draw.polygon(screen, turquoise_color, points)