

import esper
from src.ecs.components.c_player_score import CPlayerScore
from src.ecs.components.c_special_charge import CSpecialCharge
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.create.prefab_creator import create_explosion


def system_collision_enemy_bullet(world: esper.World, pl_special_charge: CSpecialCharge, explosion_info: dict):
    components_enemy = world.get_components(CSurface, CTransform, CTagEnemy)
    components_bullet = world.get_components(CSurface, CTransform, CTagBullet)
    score_component = world.get_component(CPlayerScore)

    for enemy_entity, (c_s, c_t, _) in components_enemy:
        ene_rect = c_s.area.copy()
        ene_rect.topleft = c_t.pos
        for bullet_entity, (c_b_s, c_b_t, _) in components_bullet:
            bull_rect = c_b_s.area.copy()
            bull_rect.topleft = c_b_t.pos
            if ene_rect.colliderect(bull_rect):
                world.delete_entity(enemy_entity)
                world.delete_entity(bullet_entity)
                for _, (s_c) in score_component:
                    s_c.score += 1000
                    s_c.kills += 1
                create_explosion(world,c_t.pos, explosion_info)
                pl_special_charge.add_charge()
