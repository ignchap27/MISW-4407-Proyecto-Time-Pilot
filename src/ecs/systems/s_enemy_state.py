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

        anim = c_a.animations_list[c_a.curr_anim]
        if anim.start == anim.end:
            set_frame_by_angle(c_a, c_v.vel)

def set_frame_by_angle(c_anim: CAnimation, velocity: pygame.Vector2):
    if velocity.length_squared() == 0:
        frame = 0  # Default frame if not moving
    else:
        angle = velocity.angle_to(pygame.Vector2(1, 0))  # 0° = right
        angle = (angle + 360) % 360  # Normalize to 0–359°
        frame = round((angle / 360) * c_anim.number_frames) % c_anim.number_frames
    
    c_anim.curr_frame = frame


def _get_direction_name(velocity: pygame.Vector2) -> str:
    if velocity.length_squared() == 0:
        return "MOVE_UP"  # Default idle direction

    angle = velocity.angle_to(pygame.Vector2(0, -1))  # 0° = up
    angle = (angle + 360) % 360

    if 337.5 <= angle or angle < 22.5:
        return "MOVE_UP"
    elif 22.5 <= angle < 67.5:
        return "MOVE_UP_DIAGLEFT"
    elif 67.5 <= angle < 112.5:
        return "MOVE_LEFT"
    elif 112.5 <= angle < 157.5:
        return "MOVE_LEFT_DIAGDOWN"
    elif 157.5 <= angle < 202.5:
        return "MOVE_DOWN"
    elif 202.5 <= angle < 247.5:
        return "MOVE_DOWN_DIAGRIGHT"
    elif 247.5 <= angle < 292.5:
        return "MOVE_RIGHT"
    elif 292.5 <= angle < 337.5:
        return "MOVE_RIGHT_DIAGUP"
    
    

