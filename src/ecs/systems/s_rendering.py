# src/ecs/systems/s_rendering.py
import esper, pygame
from src.ecs.components.c_transform   import CTransform
from src.ecs.components.c_surface     import CSurface
from src.ecs.components.tags.c_tag_cloud import CTagCloud

# tabla de prioridad: menor número = más al fondo
_LAYER_CLOUD = {"small": 0, "medium": 1, "large": 3}
DEFAULT_LAYER = 2          # avión, balas, etc.

def system_rendering(world: esper.World, screen: pygame.Surface) -> None:
    render_queue = []

    for ent, (c_t, c_s) in world.get_components(CTransform, CSurface):

        # --- decide la capa ------------------------------------------
        layer = DEFAULT_LAYER
        if world.has_component(ent, CTagCloud):
            size = world.component_for_entity(ent, CTagCloud).get_size()
            layer = _LAYER_CLOUD.get(size, DEFAULT_LAYER)

        # guarda todo para ordenarlo luego
        render_queue.append((layer, c_s.surf, c_t.pos, c_s.area))

    # --- pinta del fondo (layer bajo) al frente (layer alto) ----------
    render_queue.sort(key=lambda item: item[0])

    for _, surf, pos, area in render_queue:
        screen.blit(surf, pos, area=area)
