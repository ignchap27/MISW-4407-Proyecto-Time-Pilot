
import esper
import pygame

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface

def system_rendering(world:esper.World, screen:pygame.Surface):
    components = world.get_components(CTransform, CSurface)
    
    c_t:CTransform
    c_s:CSurface
    for _, (c_t, c_s) in components:
        screen.blit(c_s.surf, c_t.pos, area=c_s.area)
        debug_area = c_s.area.copy()
        debug_area.topleft = c_t.pos.copy()
        #pygame.draw.rect(screen, pygame.Color(255,255,255), debug_area, 1)