import esper
from src.ecs.components.c_boss_health import CBossHealth
from src.ecs.components.c_player_score import CPlayerScore
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_boss import CTagBoss
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.create.prefab_creator import create_boss_explosion, create_explosion


def system_collision_enemy_bullet(world: esper.World, explosion_info: dict, boss_explosion_info):
    components_enemy = world.get_components(CSurface, CTransform, CTagEnemy)
    components_boss = world.get_components(CSurface, CTransform, CTagBoss)
    components_bullet = world.get_components(CSurface, CTransform, CTagBullet)
    score_component = world.get_component(CPlayerScore)

    bullets_to_delete = set()

    for enemy_entity, (c_s, c_t, _) in components_enemy:
        ene_rect = c_s.area.copy()
        ene_rect.topleft = c_t.pos
        for bullet_entity, (c_b_s, c_b_t, _) in components_bullet:
            if bullet_entity in bullets_to_delete:
                continue
            bull_rect = c_b_s.area.copy()
            bull_rect.topleft = c_b_t.pos
            if ene_rect.colliderect(bull_rect):
                if world.entity_exists(enemy_entity):
                    world.delete_entity(enemy_entity)
                    create_explosion(world, c_t.pos, explosion_info)
                bullets_to_delete.add(bullet_entity)
                for _, (s_c) in score_component:
                    s_c.score += 1000
                    s_c.kills += 1

    for boss_entity, (c_s, c_t, _) in components_boss:
        ene_rect = c_s.area.copy()
        ene_rect.topleft = c_t.pos
        boss_defeated_this_frame = False
        for bullet_entity, (c_b_s, c_b_t, _) in components_bullet:
            if bullet_entity in bullets_to_delete:
                continue
            bull_rect = c_b_s.area.copy()
            bull_rect.topleft = c_b_t.pos
            if ene_rect.colliderect(bull_rect):
                bullets_to_delete.add(bullet_entity)
                
                boss_health_component = world.component_for_entity(boss_entity, CBossHealth)
                boss_health_component.take_damage(2)
                
                if boss_health_component.current_health <= 0:
                    boss_defeated_this_frame = True

                    for spawner_entity, spawner_component in world.get_component(CEnemySpawner):
                        spawner_component.is_active = False

                    enemies_to_explode = []
                    for other_enemy_entity, (other_c_t, _) in world.get_components(CTransform, CTagEnemy):
                        if other_enemy_entity != boss_entity:
                            enemies_to_explode.append((other_enemy_entity, other_c_t.pos.copy()))
                    
                    for other_enemy_entity, other_enemy_pos in enemies_to_explode:
                        if world.entity_exists(other_enemy_entity):
                            world.delete_entity(other_enemy_entity)
                            create_explosion(world, other_enemy_pos, explosion_info)
                            for _, (s_c) in score_component:
                                s_c.score += 100
                                s_c.kills += 1

                    if world.entity_exists(boss_entity):
                        world.delete_entity(boss_entity)
                    for _, (s_c) in score_component:
                        s_c.score += 5000
                        s_c.kills += 1
                    create_boss_explosion(world, c_t.pos, boss_explosion_info)
                    break
        
        if boss_defeated_this_frame:
            break

    for bullet_entity in bullets_to_delete:
        if world.entity_exists(bullet_entity):
            world.delete_entity(bullet_entity)