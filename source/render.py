'''
render.py: rendering handling and calculations
'''

import pygame
import library
from source.objects import *
from source.constants import *

pygame.font.init()
font = pygame.font.SysFont("Arial", 24)
console_font = pygame.font.SysFont("consolas", 20)

# converts from world coordinates to pygame screen coordinates, accounting for camera position and zoom
def camera_transfrom(texture, xy):

    texture = texture.copy()
    texture = pygame.transform.scale(texture,
        (texture.get_width() * camera.zoom, texture.get_height() * camera.zoom)
    )
    xy = (
        camera.zoom * (xy[0] - camera.xy[0]),
        Window.height - camera.zoom * (xy[1] - camera.xy[1]) - texture.get_height()
    )
    return (texture, xy )

def render_grid():
    step_size = 100
    start_x = int(camera.zoom * (-camera.xy[0] % step_size))
    start_y = int(camera.zoom * (-camera.xy[1] % step_size))
    render_step_size = int(step_size * camera.zoom)

    world_x = camera.xy[0] + (step_size - (camera.xy[0] % step_size)) - (step_size if (camera.xy[0] % step_size == 0) else 0)
    world_y = camera.xy[1] + (step_size - (camera.xy[1] % step_size)) - (step_size if (camera.xy[1] % step_size == 0) else 0)

    for render_x in range(start_x, Window.width, render_step_size):
        pygame.draw.line(Window.screen, pygame.Color('grey'), (render_x, 0), (render_x, Window.height), width=1)

    for render_y in range(start_y, Window.width, render_step_size):
        pygame.draw.line(Window.screen, pygame.Color('grey'), (0, Window.height - render_y), (Window.width, Window.height - render_y), width=1)

    if abs(start_x - start_y) < 20:
        # console_log('are wii gona have a problem here?')
        offset = (step_size // 5)
        library.simple_text(console_font, pygame.Color('grey'), str(world_x),
            (start_x + offset), Window.height - console_font.get_height())
        world_x += step_size
        library.simple_text(console_font, pygame.Color('grey'), str(world_y),
            0, Window.height - (start_y) - console_font.get_height() - offset)
        world_y += step_size

        for render_x in range(start_x + render_step_size, Window.width, render_step_size):
            library.simple_text(console_font, pygame.Color('grey'), str(world_x),
                render_x, Window.height - console_font.get_height())
            world_x += step_size

        for render_y in range(start_y + render_step_size, Window.width, render_step_size):
            library.simple_text(console_font, pygame.Color('grey'), str(world_y),
                0, Window.height - render_y - console_font.get_height())
            world_y += step_size
    else:
        for render_x in range(start_x, Window.width, render_step_size):
            library.simple_text(console_font, pygame.Color('grey'), str(world_x),
                render_x, Window.height - console_font.get_height())
            world_x += step_size

        for render_y in range(start_y, Window.width, render_step_size):
            library.simple_text(console_font, pygame.Color('grey'), str(world_y),
                0, Window.height - render_y - console_font.get_height())
            world_y += step_size

# Coming soon: we will no longer store hitbox as a pygame texture,
# all we need is a series of points
def render_hitbox(): pass

def render_camera_deadzone():
    pygame.draw.rect(Window.screen, pygame.Color('black'),
        pygame.Rect(
            camera.deadzone_x0, Window.height - camera.deadzone_y0 - camera.deadzone_h,
            camera.deadzone_w, camera.deadzone_h), 2
        )

def render_item(item):
    Window.screen.blit(*camera_transfrom(item.texture, item.xy))

def render_items():
    Window.screen.fill(pygame.Color('darkcyan'))

    # conditional rendering
    # if world.editing:
    #     Window.screen.blit(*camera_transfrom(world.next_box.texture, world.mouse_xy))

    # for box in world.boxes:
    #     Window.screen.blit(*camera_transfrom(box.texture, box.xy))
    for surface in world.surfaces:
        Window.screen.blit(*camera_transfrom(surface.texture, surface.xy))

    # how player texture is transformed relative to the hitbox
    # this might be needless initialization
    player_tex = player.get_texture()
    player_tex_xy = [ player.xy[0], player.xy[1] ]

    match player.animation:
        case Animations.TURN:
            player_tex = player.get_texture()
            player_tex_xy = [ player.xy[0] - 70, player.xy[1] - 20 ]
        case Animations.WALK | Animations.NONE:
            match player.direction:
                case States.RIGHT:
                    player_tex = player.get_texture()
                    player_tex_xy = [ player.xy[0] - 90, player.xy[1] - 20 ]
                case States.LEFT:
                    player_tex = pygame.transform.flip(player.get_texture(), True, False)
                    player_tex_xy = [ player.xy[0] - 40, player.xy[1] - 20 ]

    Window.screen.blit(*camera_transfrom(player_tex, player_tex_xy))

    for virus in world.viruses:
        Window.screen.blit(*camera_transfrom(virus.texture, virus.xy))
    # console_log('I wanna render the viruses')

    # if player.sucking:
    if True:
        # console_log('sucking')
        Window.screen.blit(*camera_transfrom(
            player.needle.texture,
            # player.needle.xy
            (player.needle.get_x0(), player.needle.get_y0())
        ))

    if game.show_grid:
        render_grid()
        Window.screen.blit(*camera_transfrom(player.texture, player.xy))
        render_camera_deadzone()

    if game.show_console:
        library.simple_text(console_font, pygame.Color('blue'), "\n".join(Debug.console), 10, 100)

    Window.total_frames += 1
    pygame.display.flip()
