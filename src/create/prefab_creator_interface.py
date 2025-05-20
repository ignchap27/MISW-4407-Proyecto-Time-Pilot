import esper
import pygame
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.engine.service_locator import ServiceLocator

def create_text(world: esper.World, text: str, size: int, color: pygame.Color, 
                position: pygame.Vector2, alignment: str):
    text_entity = world.create_entity()
    
    # Obtener la fuente desde el servicio
    font = ServiceLocator.fonts_service.get('assets/fnt/PressStart2P.ttf', size)
    
    # Renderizar el texto
    text_surface, text_rect = font.render(text, color)
    
    # Ajustar posición según alineación
    if alignment == "center":
        position.x -= text_rect.width // 2
    elif alignment == "right":
        position.x -= text_rect.width
    
    # Añadir componentes
    world.add_component(text_entity, CTransform(position))
    world.add_component(text_entity, CSurface.from_surface(text_surface))