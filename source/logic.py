'''
logic.py: includes gameplay logic, collisions, animation
'''

import pygame
# import library
from source.objects import *
from source.constants import *

## WORLD STATE & PHYSICS ===================================================================

def boxes_intersect(box0: Box, box1: Box):
    return ((box0.get_x0() <= box1.get_x1()) and (box0.get_x1() >= box1.get_x0())
        and (box0.get_y0() <= box1.get_y1()) and (box0.get_y1() >= box1.get_y0()))

def update_momentum():
    if player.jumping:
        player.x_momentum = 5 + min(player.x_momentum_max, player.x_momentum + player.x_momentum_inc)
    else:
        player.x_momentum = min(player.x_momentum_max, player.x_momentum + player.x_momentum_inc)

def virus_bounce(virus: Virus):
    match virus.xy_direction:
        case [1, 1]:
            if virus.get_y1() >= virus.container.get_y1():
                virus.xy_direction[1] = -1
            if virus.get_x1() >= virus.container.get_x1():
                virus.xy_direction[0] = -1
        case [-1, 1]:
            if virus.get_y1() >= virus.container.get_y1():
                virus.xy_direction[1] = -1
            if virus.xy[0] <= virus.container.xy[0]:
                virus.xy_direction[0] = 1
        case [1, -1]:
            if virus.xy[1] <= virus.container.xy[1]:
                virus.xy_direction[1] = 1
            if virus.get_x1() >= virus.container.get_x1():
                virus.xy_direction[0] = -1
        case [-1, -1]:
            if virus.xy[1] <= virus.container.xy[1]:
                virus.xy_direction[1] = 1
            if virus.xy[0] <= virus.container.xy[0]:
                virus.xy_direction[0] = 1

    virus.xy[0] += virus.speed * virus.xy_direction[0]
    virus.xy[1] += virus.speed * virus.xy_direction[1]

def track_camera():
    player_cam_x0 = player.get_x0() - camera.xy[0]
    player_cam_x1 = player.get_x1() - camera.xy[0]

    if player_cam_x0 < camera.deadzone_x0:
        camera.xy[0] -= camera.deadzone_x0 - player_cam_x0
    if player_cam_x1 > camera.deadzone_x1:
        camera.xy[0] += player_cam_x1 - camera.deadzone_x1

## ANIMATIONS ===================================================================

def manage_animations():
    player.frame_hold += 1

    if player.frame_hold >= player.animation_durations[player.animation][player.frame]:
        # what this generally means is - should the animation loop or terminate to something else
        if player.animation == Animations.TURN:
            if player.movement != [0, 0]:
                player.set_animation(Animations.WALK)
            else:
                player.set_animation(Animations.NONE)
        else:
            player.frame_hold = 0
            player.frame = (player.frame + 1) % len(player.animations[player.animation])

## MAIN ===================================================================

def update_world():

    manage_animations()
    track_camera()

    grounded_before = player.grounded

    if player.jumping:
        player.y_momentum = max(0, player.y_momentum - player.jump_force_decrement)
        # player.set_y0(player.xy[1] + max(0, player.y_momentum))
        player.xy[1] += player.y_momentum

    # if not player.grounded: player.set_y0(player.xy[1] - world.gravity)
    if not player.grounded: player.xy[1] -= world.gravity
    player.grounded = False

    if 1 in player.movement: update_momentum()
    x_momentum = player.x_momentum if player.direction == States.RIGHT else -player.x_momentum
    player.blocked = False

    for i, surface in enumerate(world.surfaces):
        # hitting the ground collision
        if (
            (player.xy[0] < surface.get_x1() and player.get_x1() > surface.xy[0]) and
            (player.xy[1] <= surface.get_y1() ) and
            (player.xy[1] + world.gravity > surface.get_y1())
        ):
            player.grounded = True
            player.jumping = False
            # player.set_y0(surface.get_y1())
            player.xy[1] = surface.get_y1()

        # hitting a wall collision
        if (player.xy[1] < surface.get_y1() and player.get_y1() > surface.xy[1]):
            if (
                (player.get_x1() <= surface.xy[0]) and
                (player.get_x1() + x_momentum >= surface.xy[0])
            ):
                player.blocked = True
                player.set_x1(surface.xy[0])
            elif (
                (player.xy[0] >= surface.get_x1()) and
                (player.xy[0] + x_momentum <= surface.get_x1())
            ):
                player.blocked = True
                player.xy[0] = surface.get_x1()


    if (not grounded_before and player.grounded) and 1 in player.movement:
        player.set_animation(Animations.WALK)

    # if not grounded_before and player.grounded:
    #     player.x_momentum

    if not player.blocked:
        player.xy[0] += int(x_momentum)

    # sucking
    if player.sucking:
        if player.owned_virus:
            for surface in world.surfaces:
                if boxes_intersect(player.needle, surface):
                    player.owned_virus.xy[0] = player.needle.get_x0()
                    player.owned_virus.xy[1] = player.needle.get_y0()
                    player.owned_virus.container = surface
                    player.owned_virus = None
                    player.sucking = False
        else:
            for virus in world.viruses:
                if boxes_intersect(player.needle, virus):
                    virus.container = player
                    player.owned_virus = virus
                    player.sucking = False
                    break

    for virus in world.viruses:
        # console_log(virus.container)
        if virus.container == player:
            virus.xy[0] = player.xy[0]
            virus.xy[1] = player.xy[1]
        else:
            virus_bounce(virus)
