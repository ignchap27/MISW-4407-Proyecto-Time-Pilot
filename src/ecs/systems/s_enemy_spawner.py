import esper
import pygame

from src.create.prefab_creator import create_boss, create_enemy
from src.ecs.components.c_enemy_spawner import CEnemySpawner, SpawnEventData, get_random_position_outside_screen
from src.ecs.components.c_player_score import CPlayerScore
from src.ecs.components.tags.c_tag_boss import CTagBoss

def system_enemy_spawner(world: esper.World, enemies_data: dict, delta_time: float, bosses_data: dict, level_data: dict):
    components = world.get_component(CEnemySpawner)
    
    screen_width = 500 # Deberías obtener esto de una configuración global o pasarlo
    screen_height = 500

    boss_components = world.get_component(CTagBoss)
    boss_already_exists = len(list(boss_components)) > 0
    
    for _, c_spw in components:
        if not c_spw.is_active: # Comprobar si el spawner está activo
            continue # Si no está activo, saltar este spawner

        c_spw.current_time += delta_time
        
        # Procesar los eventos preestablecidos (si hay alguno)
        for spw_evt in c_spw.spawn_event_data:
            if c_spw.current_time >= spw_evt.time and not spw_evt.triggered:
                spw_evt.triggered = True
                create_enemy(world,
                             spw_evt.position,
                             enemies_data[spw_evt.enemy_type])
        
        # Procesar spawn continuo
        if c_spw.continuous_spawn:
            c_spw.time_since_last_spawn += delta_time
            if c_spw.time_since_last_spawn >= c_spw.spawn_interval:
                c_spw.time_since_last_spawn = 0
                random_pos = get_random_position_outside_screen(screen_width, screen_height)
                create_enemy(world, random_pos, enemies_data[c_spw.enemy_type])
        
        # Verificar si debemos crear un jefe # Ya no necesitamos hasattr si siempre está presente
        score_component = world.get_component(CPlayerScore)
        for _, (s_c) in score_component:
            # Numero d ekills para aparicion del boss
            if s_c.kills >= 40 and not boss_already_exists: 
                boss_name = level_data["boss"]["name"]
                boss_pos_x = level_data["boss"]["position"]["x"]
                boss_pos_y = level_data["boss"]["position"]["y"]
                boss_pos = pygame.Vector2(boss_pos_x, boss_pos_y)
                create_boss(world, boss_pos, bosses_data[boss_name])
                c_spw.boss_created = True
                # Opcional: desactivar spawn continuo cuando aparece el jefe
                # c_spw.continuous_spawn = False 
                break # Salir del bucle de score_component una vez creado el jefe