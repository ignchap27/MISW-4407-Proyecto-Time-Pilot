import esper

from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet


def system_object_movement(world: esper.World, delta_time: float, player_entity: int):
    player_velocity = world.component_for_entity(player_entity, CVelocity)

    # Mover el mundo en la dirección opuesta al jugador
    dx = -player_velocity.vel.x * delta_time
    dy = -player_velocity.vel.y * delta_time

    for ent, (c_t, c_v) in world.get_components(CTransform, CVelocity):
        if ent != player_entity and not world.has_component(ent, CTagBullet):  # No mover al jugador
            c_t.pos.x += dx
            c_t.pos.y += dy