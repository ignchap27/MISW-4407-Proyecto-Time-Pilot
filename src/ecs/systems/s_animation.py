import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_surface import CSurface

def system_animation(world:esper.World, delta_time:float):
    components = world.get_components(CSurface, CAnimation)
    for _, (c_s, c_a) in components:
        # Inicializar el área del sprite si no se ha hecho todavía
        rect_surf = c_s.surf.get_rect()
        if c_s.area.w == rect_surf.w:  # Si el ancho es igual a toda la superficie
            # Ajustar el ancho del área al ancho de un solo frame
            c_s.area.w = rect_surf.w / c_a.number_frames
            # Establecer la posición X según el frame actual
            c_s.area.x = c_s.area.w * c_a.curr_frame
        
        # Disminuir el valor de curr_time de la animación
        c_a.curr_anim_time -= delta_time
        # Cuando curr_time <= 0
        if c_a.curr_anim_time <= 0:
            # RESTAURAR EL TIEMPO
            c_a.curr_anim_time = c_a.animations_list[c_a.curr_anim].framerate
            # CAMBIO DE FRAME
            c_a.curr_frame += 1
            # Limitar el frame con sus propiedad de start y end
            if c_a.curr_frame > c_a.animations_list[c_a.curr_anim].end:
                c_a.curr_frame = c_a.animations_list[c_a.curr_anim].start
            # Calcular la nueva subarea del rectangulo de sprite
            c_s.area.x = c_s.area.w * c_a.curr_frame