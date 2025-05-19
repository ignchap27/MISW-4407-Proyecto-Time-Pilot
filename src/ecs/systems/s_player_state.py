import esper
import pygame

from src.ecs.components.c_animation import CAnimation, set_animation
from src.ecs.components.c_player_state import CPlayerState
from src.engine.service_locator import ServiceLocator


def system_player_state(world: esper.World, player_info: dict, player_angle: float, player_is_thrusting: bool):
    components = world.get_components(CPlayerState, CAnimation)
    for entity, (c_st, c_a) in components:
        direction_name = _get_direction_name_from_angle(player_angle)
        set_animation(c_a, direction_name)


def _get_direction_name_from_angle(angle_degrees: float) -> str:
    """
    Determina el nombre de la animación según el ángulo en grados.
    Pygame y Vector2.rotate(): 0 es Eje X positivo (Derecha).
    GameEngine usa: 0=UP, 90=RIGHT, 180=DOWN, 270=LEFT.
    Esta función espera el ángulo como lo define GameEngine.
    """
    
    angle_degrees %= 360
    if angle_degrees < 0:
        angle_degrees += 360

    if (angle_degrees >= 337.5 or angle_degrees < 22.5):
        return "MOVE_UP"
    elif angle_degrees < 67.5:
        return "MOVE_DIAGUP"
    elif angle_degrees < 112.5:
        return "MOVE_RIGHT"
    elif angle_degrees < 157.5:
        return "MOVE_DIAGRIGHT"
    elif angle_degrees < 202.5:
        return "MOVE_DOWN"
    elif angle_degrees < 247.5:
        return "MOVE_DIAGDOWN"
    elif angle_degrees < 292.5:
        return "MOVE_LEFT"
    elif angle_degrees < 337.5:
        return "MOVE_DIAGLEFT"
    
    return "MOVE_UP"
