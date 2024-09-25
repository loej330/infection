'''
input.py: determines inuput states
determines how game states should change depending on current input states
'''

import pygame
from source.objects import *
from source.constants import *

# pressed: this is the first frame
def pressed(input): return world.input_states[input] == States.PRESSED
def pressing(input): return world.input_states[input] == States.PRESSING
def depressed(input): return world.input_states[input] == States.DEPRESSED
def depressing(input): return world.input_states[input] == States.DEPRESSING
def pressing_or_pressed(input):
    return world.input_states[input] == States.PRESSED or world.input_states[input] == States.PRESSING
def depressing_or_depressed(input):
    return world.input_states[input] == States.DEPRESSED or world.input_states[input] == States.DEPRESSING

# made to handle edge cases where LEFT and RIGHT are held at the same time
def update_walk_state(prev_movement):
    if prev_movement == player.movement: return

    # cases where the player STARTS walking
    if prev_movement == [0, 0]:
        if player.grounded:
            player.set_animation(Animations.WALK)
        if player.movement == [1, 0]:
            player.direction = States.LEFT
        if player.movement == [0, 1] or player.movement == [1, 1]:
            player.direction = States.RIGHT

    # cases where the player turns
    if (
        ((prev_movement == [1, 1] and player.direction == States.RIGHT)
        or (prev_movement == [0, 1]))
        and player.movement == [1, 0]
    ):
        player.x_momentum = 0
        player.direction = States.LEFT
    if (
        ((prev_movement == [1, 1] and player.direction == States.LEFT)
        or (prev_movement == [1, 0]))
        and player.movement == [0, 1]
    ):
        player.x_momentum = 0
        player.direction = States.RIGHT

    # cases where the player STOPS walking
    if player.movement == [0, 0]:
        player.x_momentum = 0
        player.set_animation(Animations.NONE)

def process_input(events):
    for input, state in world.input_states.items():
        if state == States.PRESSING: world.input_states[input] = States.PRESSED
        if state == States.DEPRESSING: world.input_states[input] = States.DEPRESSED
    for e in events:
        match e.type:
            case pygame.KEYDOWN:
                # TODO: looping through every mapping fine for now but not ideal, we must consider if we should have two dictionaries that go both ways
                for input, mapping in world.mapping.items():
                    if e.key in mapping:
                        world.input_states[input] = States.PRESSING
            case pygame.KEYUP:
                for input, mapping in world.mapping.items():
                    if e.key in mapping:
                        world.input_states[input] = States.DEPRESSING
            case pygame.MOUSEBUTTONDOWN:
                for input, mapping in world.mapping.items():
                    if e.button in mapping:
                        world.input_states[input] = States.PRESSING
            case pygame.MOUSEBUTTONUP:
                for input, mapping in world.mapping.items():
                    if e.button in mapping:
                        world.input_states[input] = States.DEPRESSING
            case pygame.MOUSEWHEEL:# TEMP FIX
                camera.zoom = max(0.1, camera.zoom + (e.y * camera.zoom_rate))
                # console_log(camera.zoom)

    if pressing(Inputs.DEBUG_7):
        load_data()
    if pressing(Inputs.DEBUG_8):
        save_to_file()

    world.mouse_xy = [ *pygame.mouse.get_pos() ]
    world.mouse_xy[1] = Window.height - world.mouse_xy[1]

    if pressing(Inputs.DEBUG_1):
        if world.show_console: world.show_console= False
        else:
            world.show_console = True
            console_reset()

    if pressing(Inputs.DEBUG_2):
        world.show_grid = not world.show_grid

    if pressing(Inputs.PLACE):
        world.next_box.xy = world.mouse_xy
        world.boxes.append(world.next_box)
        world.next_box = Box()

    # handleing walking input ==================================================

    last_walking = player.movement.copy()
    last_direction = player.direction

    if pressing(Inputs.LEFT):
        player.movement[0] = True
    if pressing(Inputs.RIGHT):
        player.movement[1] = True
    if depressing(Inputs.LEFT):
        player.movement[0] = False
    if depressing(Inputs.RIGHT):
        player.movement[1] = False

    update_walk_state(last_walking)

    if player.direction != last_direction:
        player.set_animation(Animations.TURN)

    # ==========================================================================

    if pressing(Inputs.SUCK):
        player.sucking = True
    if depressing(Inputs.SUCK):
        player.sucking = False

    if pressing(Inputs.JUMP):
        if player.grounded:
            player.jumping = True
            player.grounded = False
            player.y_momentum = player.jump_force
            player.set_animation(Animations.NONE)
            # player.speed = player.jump_speed

    if pressing_or_pressed(Inputs.CAM_LEFT):
        camera.xy[0] -= int(camera.move_rate / camera.zoom)
    if pressing_or_pressed(Inputs.CAM_RIGHT):
        camera.xy[0] += int(camera.move_rate / camera.zoom)
    if pressing_or_pressed(Inputs.CAM_DOWN):
        camera.xy[1] -= int(camera.move_rate / camera.zoom)
    if pressing_or_pressed(Inputs.CAM_UP):
        camera.xy[1] += int(camera.move_rate / camera.zoom)
    if pressing(Inputs.CAM_ZOOM_IN): camera.zoom = camera.zoom + camera.zoom_rate
    if pressing(Inputs.CAM_ZOOM_OUT): camera.zoom = max(0.1, camera.zoom - camera.zoom_rate)
