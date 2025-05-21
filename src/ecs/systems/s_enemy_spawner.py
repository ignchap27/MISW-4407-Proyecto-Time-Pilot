import esper
import pygame

from src.create.prefab_creator import create_enemy
from src.ecs.components.c_enemy_spawner import CEnemySpawner, SpawnEventData, get_random_position_outside_screen

def system_enemy_spawner(world: esper.World, enemies_data: dict, delta_time: float):
    components = world.get_component(CEnemySpawner)
    
    # Dimensiones estándar de la pantalla
    screen_width = 500
    screen_height = 500
    
    for _, c_spw in components:
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
                
                # Generar posición aleatoria fuera de la pantalla
                random_pos = get_random_position_outside_screen(screen_width, screen_height)
                
                # Crear enemigo
                create_enemy(world, random_pos, enemies_data[c_spw.enemy_type])