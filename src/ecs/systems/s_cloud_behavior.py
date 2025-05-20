import pygame
import esper

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_file import CTagCloud # CTagCloud está en c_tag_file.py

def system_cloud_behavior(world: esper.World, screen: pygame.Surface):
    """
    Maneja el comportamiento de las nubes, principalmente el "wrapping" en pantalla.
    Si una nube sale por un lado de la pantalla, reaparece por el lado opuesto.
    """
    screen_rect = screen.get_rect()
    
    components = world.get_components(CTransform, CSurface, CTagCloud)

    for entity, (c_t, c_s, _) in components:
        cloud_width = c_s.surf.get_width()
        cloud_height = c_s.surf.get_height()

        # Wrapping horizontal
        if c_t.pos.x + cloud_width < 0:  # Se fue completamente por la izquierda
            c_t.pos.x = screen_rect.width
        elif c_t.pos.x > screen_rect.width:  # Se fue completamente por la derecha
            c_t.pos.x = -cloud_width
        
        # Wrapping vertical
        if c_t.pos.y + cloud_height < 0:  # Se fue completamente por arriba
            c_t.pos.y = screen_rect.height
        elif c_t.pos.y > screen_rect.height:  # Se fue completamente por abajo
            c_t.pos.y = -cloud_height