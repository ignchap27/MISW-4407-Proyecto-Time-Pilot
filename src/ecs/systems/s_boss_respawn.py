import time
import esper
import pygame
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_boss import CTagBoss

def system_boss_respawn(world: esper.World, screen: pygame.Surface, level_cfg: dict):
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    boss_spawn_data = level_cfg.get("boss")

    if not boss_spawn_data or "position" not in boss_spawn_data:
        # print("Advertencia: No se encontraron datos de posición inicial del jefe en level_cfg.")
        return

    initial_boss_pos_x = float(boss_spawn_data["position"]["x"])
    initial_boss_pos_y = float(boss_spawn_data["position"]["y"])

    for boss_entity, (c_tag_boss, c_t, c_s) in world.get_components(CTagBoss, CTransform, CSurface):
        boss_x = c_t.pos.x
        boss_y = c_t.pos.y
        boss_width = c_s.area.width
        boss_height = c_s.area.height

        # Condición para determinar si el jefe se salió por la IZQUIERDA
        exited_left = boss_x + boss_width < 0
        
        # Condiciones para determinar si el jefe se salió por ARRIBA o ABAJO
        exited_top = boss_y + boss_height < 0
        exited_bottom = boss_y > screen_height

        # Si el jefe está actualmente a la derecha de la pantalla (incluyendo su posición inicial)
        # y no se ha salido por arriba o abajo, no hacemos nada para que pueda moverse hacia la izquierda.
        if boss_x >= screen_width and not (exited_top or exited_bottom) :
            continue # Permitir que el jefe entre desde la derecha

        # Si el jefe se salió por la izquierda, arriba o abajo, lo reposicionamos.
        if exited_left or exited_top or exited_bottom:
            c_t.pos.x = initial_boss_pos_x + 100
            c_t.pos.y = initial_boss_pos_y + 100
