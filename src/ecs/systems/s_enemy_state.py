import esper
import pygame

from src.ecs.components.c_animation import CAnimation, set_animation
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_enemy import CTagEnemy

def system_enemy_state(world: esper.World):
    components = world.get_components(CTagEnemy, CAnimation, CVelocity)
    for _, (_, c_a, c_v) in components:
        direction = _get_direction_name(c_v.vel)
        set_animation(c_a, direction)

def _get_direction_name(velocity: pygame.Vector2) -> str:
    x, y = velocity.x, velocity.y
    if abs(x) < 0.1 and y < 0:
        return "MOVE_UP"
    elif abs(x) < 0.1 and y > 0:
        return "MOVE_DOWN"
    elif x < 0 and abs(y) < 0.1:
        return "MOVE_LEFT"
    elif x > 0 and abs(y) < 0.1:
        return "MOVE_RIGHT"
    elif x < 0 and y < 0:
        return "MOVE_DIAGLEFT"
    elif x < 0 and y > 0:
        return "MOVE_DIAGDOWN"
    elif x > 0 and y > 0:
        return "MOVE_DIAGRIGHT"
    elif x > 0 and y < 0:
        return "MOVE_DIAGUP"
    return "MOVE_UP"