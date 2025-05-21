import pygame
import random

class CEnemySpawner:
    def __init__(self, level_data) -> None:
        # Mantenemos compatibilidad con los eventos existentes (ahora opcional)
        self.current_time: float = 0
        self.spawn_event_data: list[SpawnEventData] = []
        
        # Nueva configuración para spawn continuo
        self.continuous_spawn = True
        self.time_since_last_spawn = 0
        self.spawn_interval = 1.0  # Segundos entre spawns
        self.enemy_type = level_data["enemy_type"] # Tipo de enemigo por defecto
        self.is_active = True

class SpawnEventData:
    def __init__(self, event_data: dict) -> None:
        self.time: float = event_data["time"]
        self.enemy_type: str = event_data["enemy_type"]
        self.position: pygame.Vector2 = pygame.Vector2(
            event_data["position"]["x"],
            event_data["position"]["y"])
        self.triggered = False

def get_random_position_outside_screen(screen_width, screen_height, margin=50) -> pygame.Vector2:
    """
    Genera una posición aleatoria fuera de la pantalla
    """
    # Elegir uno de los cuatro lados: 0=arriba, 1=derecha, 2=abajo, 3=izquierda
    side = random.randint(0, 3)
    
    if side == 0:  # Arriba
        x = random.randint(0, screen_width)
        y = -margin
    elif side == 1:  # Derecha
        x = screen_width + margin
        y = random.randint(0, screen_height)
    elif side == 2:  # Abajo
        x = random.randint(0, screen_width)
        y = screen_height + margin
    else:  # Izquierda
        x = -margin
        y = random.randint(0, screen_height)
    
    return pygame.Vector2(x, y)