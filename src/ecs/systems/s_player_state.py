import esper
import pygame
import math

from src.ecs.components.c_animation import CAnimation, set_animation
from src.ecs.components.c_player_state import CPlayerState, PlayerState
from src.ecs.components.c_velocity import CVelocity
from src.engine.service_locator import ServiceLocator


def system_player_state(world: esper.World, player_info: dict):
    components = world.get_components(CPlayerState, CAnimation, CVelocity)
    for _, (c_st, c_a, c_v) in components:
        if c_st.state == PlayerState.IDLE:
            _do_player_idle(c_st, c_a, c_v, player_info)
        elif c_st.state == PlayerState.MOVE:
            _do_player_move(c_st, c_a, c_v)


def _do_player_idle(c_st: CPlayerState, c_a: CAnimation, c_v: CVelocity, player_info: dict):
    # Usar MOVE_UP como animación por defecto cuando está quieto
    set_animation(c_a, "MOVE_UP")
    if c_v.vel.magnitude_squared() > 0:
        c_st.state = PlayerState.MOVE


def _do_player_move(c_st: CPlayerState, c_a: CAnimation, c_v: CVelocity):
    # Determinar la dirección del movimiento
    direction = _get_direction_name(c_v.vel)
    set_animation(c_a, direction)
    
    if c_v.vel.magnitude_squared() <= 0:
        c_st.state = PlayerState.IDLE


def _get_direction_name(velocity: pygame.Vector2) -> str:
    """Determina el nombre de la animación según el vector de velocidad"""
    if velocity.magnitude_squared() == 0:
        return "MOVE_UP"

    angle = math.degrees(math.atan2(-velocity.y, velocity.x)) % 360

    # Map the angle to the corresponding animation name
    if 0 <= angle < 11.25 or 348.75 <= angle <= 360:
        return "MOVE_RIGHT"
    elif 11.25 <= angle < 33.75:
        return "MOVE_RIGHT_RIGHTUP"
    elif 33.75 <= angle < 56.25:
        return "MOVE_RIGHTUP"
    elif 56.25 <= angle < 78.75:
        return "MOVE_RIGHTUP_UP"
    elif 78.75 <= angle < 101.25:
        return "MOVE_UP"
    elif 101.25 <= angle < 123.75:
        return "MOVE_UP_UPLEFT"
    elif 123.75 <= angle < 146.25:
        return "MOVE_UPLEFT"
    elif 146.25 <= angle < 168.75:
        return "MOVE_UPLEFT_LEFTUP"
    elif 168.75 <= angle < 191.25:
        return "MOVE_LEFTUP"
    elif 191.25 <= angle < 213.75:
        return "MOVE_LEFTUP_LEFT"
    elif 213.75 <= angle < 236.25:
        return "MOVE_LEFT"
    elif 236.25 <= angle < 258.75:
        return "MOVE_LEFT_LEFTDOWN"
    elif 258.75 <= angle < 281.25:
        return "MOVE_LEFTDOWN"
    elif 281.25 <= angle < 303.75:
        return "MOVE_LEFTDOWN_DOWNLEFT"
    elif 303.75 <= angle < 326.25:
        return "MOVE_DOWNLEFT"
    elif 326.25 <= angle < 348.75:
        return "MOVE_DOWNLEFT_DOWN"
    
    return "MOVE_UP"
