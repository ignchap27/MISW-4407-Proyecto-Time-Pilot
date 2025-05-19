import esper
import pygame
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_player import CTagPlayer

def system_rendering(world: esper.World, screen: pygame.Surface):
    screen_center = pygame.Vector2(screen.get_width() // 2, screen.get_height() // 2)
    components = world.get_components(CTransform, CSurface)
    for ent, (c_t, c_s) in components:
        pos = c_t.pos
        if world.has_component(ent, CTagPlayer):
            # Dibuja el jugador siempre en el centro
            pos = screen_center
        screen.blit(c_s.surf, pos, area=c_s.area)