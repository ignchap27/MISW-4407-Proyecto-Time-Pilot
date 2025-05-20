# src/ecs/systems/system_steering.py
import esper, pygame
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity  import CVelocity
from src.ecs.components.c_steer     import CSteer

def system_steering(world: esper.World, delta_time: float, player_entity: int):
    player_pos = world.component_for_entity(player_entity, CTransform).pos

    for ent, (c_t, c_v, c_s) in world.get_components(CTransform, CVelocity, CSteer):
        if ent == player_entity:
            continue

        # ---------------- SEEK puro (sin arrive) ----------------
        desired = player_pos - c_t.pos
        if desired.length_squared() == 0:
            continue                       # ya estamos encima

        desired.normalize_ip()             # dirección
        desired *= c_s.max_speed           # velocidad objetivo (constante)

        steering = desired - c_v.vel       # “fuerza” necesaria

        # Limitar la aceleración por frame
        max_force_dt = c_s.max_force * delta_time
        if steering.length_squared() > max_force_dt**2:
            steering.scale_to_length(max_force_dt)

        # Aplicar aceleración y limitar velocidad final
        c_v.vel += steering
        if c_v.vel.length_squared() > c_s.max_speed**2:
            c_v.vel.scale_to_length(c_s.max_speed)
