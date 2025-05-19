import esper
import pygame

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
    x, y = velocity.x, velocity.y
    
    # Determinar los ángulos principales
    if abs(x) < 0.1 and y < 0:
        return "MOVE_UP"
    elif abs(x) < 0.1 and y > 0:
        return "MOVE_DOWN"
    elif x < 0 and abs(y) < 0.1:
        return "MOVE_LEFT"
    elif x > 0 and abs(y) < 0.1:
        return "MOVE_RIGHT"
    
    # Determinar las diagonales
    elif x < 0 and y < 0:
        return "MOVE_DIAGLEFT"
    elif x < 0 and y > 0:
        return "MOVE_DIAGDOWN"
    elif x > 0 and y > 0:
        return "MOVE_DIAGRIGHT"
    elif x > 0 and y < 0:
        return "MOVE_DIAGUP"
    
    # Por defecto
    return "MOVE_UP"
