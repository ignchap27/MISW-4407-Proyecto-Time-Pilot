import random
import pygame
import esper

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_special_charge import CSpecialCharge
from src.ecs.components.c_steer import CSteer
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_file import CTagCloud
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_fireball import CTagFireball
from src.ecs.components.tags.c_tag_explosion import CTagExplosion
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_player_state import CPlayerState
from src.engine.service_locator import ServiceLocator


def create_square(world: esper.World, size: pygame.Vector2,
                  pos: pygame.Vector2, vel: pygame.Vector2, col: pygame.Color) -> int:
    cuad_entity = world.create_entity()
    world.add_component(cuad_entity,
                        CSurface(size, col))
    world.add_component(cuad_entity,
                        CTransform(pos))
    world.add_component(cuad_entity,
                        CVelocity(vel))
    return cuad_entity


def create_sprite(world: esper.World, pos: pygame.Vector2, vel: pygame.Vector2,
                  surface: pygame.Surface) -> int:
    sprite_entity = world.create_entity()
    world.add_component(sprite_entity,
                        CTransform(pos))
    world.add_component(sprite_entity,
                        CVelocity(vel))
    world.add_component(sprite_entity,
                        CSurface.from_surface(surface))
    return sprite_entity


# def create_enemy_square(world: esper.World, pos: pygame.Vector2, enemy_info: dict):
#     enemy_surface = ServiceLocator.images_service.get(enemy_info["image"])
#     vel = enemy_info["velocity_chase"]
#     velocity = pygame.Vector2(random.choice([-vel, vel]), random.choice([-vel, vel]))

#     enemy_entity = create_sprite(world, pos, velocity, enemy_surface)
#     world.add_component(enemy_entity, CTagEnemy("Bouncer"))
#     ServiceLocator.sounds_service.play(enemy_info["sound"])

def create_enemy(world: esper.World, pos: pygame.Vector2, enemy_info: dict):
    enemy_surface = ServiceLocator.images_service.get(enemy_info["image"])
    num_frames = enemy_info["animations"]["number_frames"]
    original_size = enemy_surface.get_size()
    frame_width = original_size[0] // num_frames
    frame_height = original_size[1]
    new_frame_width = frame_width * 2
    new_frame_height = frame_height * 2
    new_sheet_width = new_frame_width * num_frames
    enemy_surface = pygame.transform.scale(enemy_surface, (new_sheet_width, new_frame_height))
    
    # Asigna una velocidad aleatoria o fija
    speed = enemy_info.get("velocity", 100)
    angle = random.uniform(0, 2 * 3.14159)
    velocity = pygame.Vector2(speed, 0).rotate_rad(angle)
    enemy_entity = create_sprite(world, pos, velocity, enemy_surface)

    c_anim = CAnimation(enemy_info["animations"])
    world.add_component(enemy_entity, c_anim)
    world.add_component(enemy_entity, CTagEnemy("normal"))
    world.add_component(enemy_entity, CSteer())

    # Ajustar el área del sprite para mostrar solo el primer frame correctamente
    c_surf = world.component_for_entity(enemy_entity, CSurface)
    if c_surf is not None and c_anim is not None and c_anim.number_frames > 0:
        sprite_sheet_width = c_surf.surf.get_width()
        frame_width = sprite_sheet_width / c_anim.number_frames
        c_surf.area.width = int(frame_width)
        c_surf.area.x = int(frame_width * c_anim.curr_frame)


def create_player_square(world: esper.World, player_info: dict, player_lvl_info: dict) -> int:
    player_sprite = ServiceLocator.images_service.get(player_info["image"])
    num_frames = player_info["animations"]["number_frames"]
    # Obtener dimensiones del primer frame
    original_size = player_sprite.get_size()
    frame_width = original_size[0] // num_frames
    frame_height = original_size[1]
    # Calcular nuevo tamaño (doble del original)
    new_frame_width = frame_width * 2
    new_frame_height = frame_height * 2
    new_sheet_width = new_frame_width * num_frames
    # Escalar la hoja completa de sprites
    player_sprite = pygame.transform.scale(player_sprite, (new_sheet_width, new_frame_height))
    
    size = (player_sprite.get_size()[0] / num_frames, player_sprite.get_size()[1])
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - (size[0] / 2),
                         player_lvl_info["position"]["y"] - (size[1] / 2))
    vel = pygame.Vector2(0, 0)
    player_entity = create_sprite(world, pos, vel, player_sprite)
    
    # Ajustar manualmente el ancho del área del sprite antes de seguir
    c_surf = world.component_for_entity(player_entity, CSurface)
    c_anim = CAnimation(player_info["animations"])
    world.add_component(player_entity, c_anim)
    
    # Inicializar correctamente el área del sprite
    sprite_sheet_width = c_surf.surf.get_width()
    frame_width = sprite_sheet_width / c_anim.number_frames
    c_surf.area.width = int(frame_width)
    c_surf.area.x = int(frame_width * c_anim.curr_frame)
    
    # Reposicionar el jugador ahora que conocemos el ancho real
    c_transform = world.component_for_entity(player_entity, CTransform)
    c_transform.pos.x = player_lvl_info["position"]["x"] - (c_surf.area.width / 2)
    c_transform.pos.y = player_lvl_info["position"]["y"] - (c_surf.area.height / 2)
    
    # Añadir el resto de componentes
    world.add_component(player_entity, CTagPlayer())
    world.add_component(player_entity, CPlayerState())
    world.add_component(player_entity, CSpecialCharge())
    
    return player_entity


def create_enemy_spawner(world: esper.World, level_data: dict):
    spawner_entity = world.create_entity()
    world.add_component(spawner_entity,
                        CEnemySpawner(level_data["enemy_spawn_events"]))


def create_input_player(world: esper.World):
    input_left = world.create_entity()
    input_right = world.create_entity()
    input_up = world.create_entity()
    input_down = world.create_entity()

    world.add_component(input_left,
                        CInputCommand("PLAYER_LEFT", pygame.K_LEFT))
    world.add_component(input_right,
                        CInputCommand("PLAYER_RIGHT", pygame.K_RIGHT))
    world.add_component(input_up,
                        CInputCommand("PLAYER_UP", pygame.K_UP))
    world.add_component(input_down,
                        CInputCommand("PLAYER_DOWN", pygame.K_DOWN))

    input_fire = world.create_entity()
    world.add_component(input_fire,
                        CInputCommand("PLAYER_FIRE", pygame.BUTTON_LEFT))
    input_special = world.create_entity()
    world.add_component(input_special,
                        CInputCommand("SPECIAL_ATTACK", pygame.BUTTON_RIGHT))


def create_bullet(world: esper.World,
                  mouse_pos: pygame.Vector2,
                  player_pos: pygame.Vector2,
                  player_size: pygame.Vector2,
                  bullet_info: dict):
    bullet_size = pygame.Vector2(4, 4)
    color = pygame.Color(255, 255, 255)
    pos = pygame.Vector2(player_pos.x + (player_size[0] / 2) - (bullet_size[0] / 2),
                         player_pos.y + (player_size[1] / 2) - (bullet_size[1] / 2))
    vel = (mouse_pos - player_pos)
    vel = vel.normalize() * bullet_info["velocity"]

    bullet_entity = create_square(world, bullet_size, pos, vel, color)
    world.add_component(bullet_entity, CTagBullet())
    ServiceLocator.sounds_service.play(bullet_info["sound"])

def create_cloud(world: esper.World,
                 pos: pygame.Vector2, 
                 vel: pygame.Vector2,
                 cloud_type: str,
                 cloud_info: dict):
    if cloud_type == "small":
        img_path = "assets/img/clouds_small.png"
    elif cloud_type == "medium_A":
        img_path = "assets/img/clouds_medium_A.png"
    elif cloud_type == "medium_B":
        img_path = "assets/img/clouds_medium_B.png"
    elif cloud_type == "large":
        img_path = "assets/img/clouds_large.png"
    
    cloud_surface = ServiceLocator.images_service.get(img_path)
    
    num_frames = cloud_info[cloud_type]["animations"]["number_frames"]
    original_size = cloud_surface.get_size()
    frame_width = original_size[0] // num_frames
    frame_height = original_size[1]
    
    new_frame_width = frame_width * 2
    new_frame_height = frame_height * 2
    new_sheet_width = new_frame_width * num_frames
    
    # Escalar la hoja completa de sprites
    cloud_surface = pygame.transform.scale(cloud_surface, (new_sheet_width, new_frame_height))
    
    cloud_entity = create_sprite(world, pos, vel, cloud_surface)
    world.add_component(cloud_entity, CTagCloud())
    c_anim = CAnimation(cloud_info[cloud_type]["animations"])
    world.add_component(cloud_entity, c_anim)

def create_fireball(world: esper.World,
                  direction: pygame.Vector2,
                  player_pos: pygame.Vector2,
                  player_size: pygame.Vector2,
                  fireball_info: dict):
    bullet_surface = ServiceLocator.images_service.get(fireball_info["image"])
    bullet_size = bullet_surface.get_rect().size
    pos = pygame.Vector2(player_pos.x + (player_size[0] / 2) - (bullet_size[0] / 2),
                         player_pos.y + (player_size[1] / 2) - (bullet_size[1] / 2))
    vel = (direction - player_pos)
    vel = vel.normalize() * fireball_info["velocity"]

    bullet_entity = create_sprite(world, pos, vel, bullet_surface)
    world.add_component(bullet_entity, CTagFireball())
    ServiceLocator.sounds_service.play(fireball_info["sound"])
                    


def create_explosion(world: esper.World, pos: pygame.Vector2, explosion_info: dict):
    explosion_surface = ServiceLocator.images_service.get(explosion_info["image"])
    vel = pygame.Vector2(0, 0)

    explosion_entity = create_sprite(world, pos, vel, explosion_surface)
    world.add_component(explosion_entity, CTagExplosion())
    world.add_component(explosion_entity,
                        CAnimation(explosion_info["animations"]))
    ServiceLocator.sounds_service.play(explosion_info["sound"])
    return explosion_entity
