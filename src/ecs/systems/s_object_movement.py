import esper
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_cloud import CTagCloud
from src.ecs.components.tags.c_tag_enemy import CTagEnemy

def system_object_movement(world: esper.World, delta_time: float, player_entity: int):
    player_velocity = world.component_for_entity(player_entity, CVelocity)

    # Tomamos solo la dirección (normalizada)
    direction = player_velocity.vel
    if direction.length_squared() == 0:
        return  # No mover el mundo si no hay input

    direction = direction.normalize()  # Normaliza el vector (longitud 1)
    scroll_speed = 200  # Tu velocidad fija deseada para el mundo

    dx = -direction.x * scroll_speed * delta_time
    dy = -direction.y * scroll_speed * delta_time

    for ent, (c_t, c_v) in world.get_components(CTransform, CVelocity):
        if world.has_component(ent, CTagCloud) or world.has_component(ent, CTagEnemy):
            c_t.pos.x += dx
            c_t.pos.y += dy
