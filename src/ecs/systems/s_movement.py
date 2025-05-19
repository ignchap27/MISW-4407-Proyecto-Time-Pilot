import esper
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_player import CTagPlayer

def system_movement(world: esper.World, delta_time: float, scroll_vector):
    components = world.get_components(CTransform, CVelocity)
    for ent, (c_t, c_v) in components:
        # Si es el jugador, no lo muevas (solo rota en otro sistema)
        if world.has_component(ent, CTagPlayer):
            continue
        # Mueve todo lo demás con su velocidad + scroll
        c_t.pos.x += (c_v.vel.x + scroll_vector.x) * delta_time
        c_t.pos.y += (c_v.vel.y + scroll_vector.y) * delta_time