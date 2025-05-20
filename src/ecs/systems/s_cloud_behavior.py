# src/ecs/systems/s_cloud_behavior.py
import pygame, esper
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface   import CSurface
from src.ecs.components.c_velocity  import CVelocity
from src.ecs.components.tags.c_tag_cloud import CTagCloud

def system_cloud_behavior(world: esper.World, screen: pygame.Surface):
    """Parallax de nubes: tamaño ↔ velocidad y wrapping de pantalla."""
    screen_rect = screen.get_rect()

    for _, (c_t, c_s, c_v, c_cloud) in world.get_components(
        CTransform, CSurface, CVelocity, CTagCloud
    ):
        if c_v.vel.length_squared() == 0:
            base_speed = 10                         # px/seg para nubes medianas
            size = c_cloud.get_size()

            if size == "small":   speed = 1.0 * base_speed   # más lento
            elif size == "medium": speed = 2.0 * base_speed  # velocidad media
            elif size == "large":  speed = 3.5 * base_speed  # más rápido
            else:                  speed = base_speed        # fallback

            # Todas viajan de derecha a izquierda; ajusta a gusto
            c_v.vel = pygame.Vector2(-speed, 0)

        w, h = c_s.area.size

        if c_t.pos.x + w < 0:          # salió por la izquierda
            c_t.pos.x = screen_rect.width
        elif c_t.pos.x > screen_rect.width:
            c_t.pos.x = -w

        if c_t.pos.y + h < 0:          # salió por arriba
            c_t.pos.y = screen_rect.height
        elif c_t.pos.y > screen_rect.height:
            c_t.pos.y = -h
