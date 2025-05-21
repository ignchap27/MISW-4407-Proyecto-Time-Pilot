import esper
import pygame
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_ui import CTagUi
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
    world.add_component(text_entity, CTagUi())
    
def create_space(world: esper.World, size: pygame.Vector2,
                  pos: pygame.Vector2,
                  col: pygame.Color) -> int:
    space_entity = world.create_entity()
    world.add_component(space_entity,
                        CSurface(size, col))
    world.add_component(space_entity,
                        CTransform(pos))
    world.add_component(space_entity, CTagUi())
    
def create_icon(world: esper.World,
                image_path_or_surface,
                position: pygame.Vector2,
                scale: tuple[int, int] | None = None) -> int:

    if isinstance(image_path_or_surface, str):
        surf = ServiceLocator.images_service.get(image_path_or_surface)
    else:
        surf = image_path_or_surface.copy()

    if scale is not None:
        surf = pygame.transform.scale(surf, scale)

    icon_ent = world.create_entity()
    world.add_component(icon_ent, CTransform(position))
    world.add_component(icon_ent, CSurface.from_surface(surf))
    world.add_component(icon_ent, CTagUi())