

import esper
from src.ecs.components.c_special_charge import CSpecialCharge
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_fireball import CTagFireball
from src.create.prefab_creator import create_explosion


def system_collision_enemy_fireball(world: esper.World, pl_special_charge: CSpecialCharge, explosion_info: dict):
    components_enemy = world.get_components(CSurface, CTransform, CTagEnemy)
    components_fireball = world.get_components(CSurface, CTransform, CTagFireball)

    for enemy_entity, (c_s, c_t, _) in components_enemy:
        ene_rect = c_s.area.copy()
        ene_rect.topleft = c_t.pos
        for fireball_entity, (c_b_s, c_b_t, _) in components_fireball:
            bull_rect = c_b_s.area.copy()
            bull_rect.topleft = c_b_t.pos
            if ene_rect.colliderect(bull_rect):
                world.delete_entity(enemy_entity)
                world.delete_entity(fireball_entity)
                create_explosion(world, c_t.pos, explosion_info)
                pl_special_charge.add_charge()
