'''
objects.py: All data associated with the world, objects, and player
'''

from __future__ import annotations
import time, pygame, sys, pickle, os
from dataclasses import dataclass
from collections import deque
from source.constants import *

class Window():
    screen: pygame.Surface
    width: int
    height: int
    total_frames = 0

class Debug():
    console = deque([ 'Welcome to debug mode!' ])
    max_lines = 10
def console_log(data):
    Debug.console.append(str(data))
    while len(Debug.console) > Debug.max_lines: Debug.console.popleft()
def console_reset():
    Debug.console = deque([ 'Welcome to debug mode!' ])

class Camera():
    xy = [0, 0] # camera's position in world coordinates
    move_rate = 10
    zoom = 1.0
    zoom_rate = 0.1

    deadzone_x0, deadzone_y0 = [ 200, 200 ]
    deadzone_w, deadzone_h = [500, 300]
    deadzone_x1, deadzone_y1 = [ deadzone_x0 + deadzone_w, deadzone_y0 + deadzone_h ]


class Box():
    xy = [0, 300]
    wh = [100, 100]
    weight = 10
    color = pygame.Color('blue')
    anchor: None

    def __init__(self, **args):
        for key, val in args.items(): setattr(self, key, val)

        self.texture = pygame.Surface((self.wh), pygame.SRCALPHA)
        pygame.draw.rect(self.texture, self.color, pygame.Rect(0, 0, *self.wh), 4)

    def get_x0(self): return self.xy[0]
    def get_y0(self): return self.xy[1]
    def get_x1(self): return self.xy[0] + self.wh[0]
    def get_y1(self): return self.xy[1] + self.wh[1]

    def set_x1(self, x1): self.xy[0] = x1 - self.wh[0]
    def set_y1(self, y1): self.xy[1] = y1 - self.wh[1]

class Player(Box):
    def __init__(self, **args):
        super().__init__(
            color = pygame.Color('orange'),
            wh = [130, 130],
            xy = [400, 201],
        )
        # super().__init__(**args)
        self.needle = Box(
            wh = [10, 80],
            color = pygame.Color('purple')
        )
        self.needle.get_x0 = lambda: self.xy[0] + (self.wh[0]//2) - (self.needle.wh[0]//2)
        self.needle.get_y0 = lambda: self.xy[1] - self.needle.wh[1]
        self.needle.get_x1 = lambda: self.needle.get_x0() + self.needle.wh[0]
        self.needle.get_y1 = lambda: self.needle.get_y0() + self.needle.wh[1]
        # needed because the needle's position depends on player's

    # POSSIBLY NEEDED:
        # indication of weather an animation should loop or fallback to something after playing
        # texture offset information relative to the hitbox for each frame
    animations = {
        Animations.NONE: tuple((pygame.image.load(f'assets/player0000.png'),)), # texture to use when no animation is occuring
        Animations.WALK: tuple((pygame.image.load(f'assets/player-walk{i:04d}.png') for i in range(3))),
        Animations.TURN: tuple((pygame.image.load(f'assets/player-turn{i:04d}.png') for i in range(1))),
    }
    animation_durations = { # for tweaking the pacing of animation frames
        Animations.NONE: (1, ),
        Animations.WALK: (8, 4, 4, 8),
        Animations.TURN: (4, )
    }
    animation = Animations.NONE
    frame = 0
    frame_hold = 0

    # physics
    x_momentum = 0.0
    x_momentum_inc = 0.3
    x_momentum_max = 8.0
    y_momentum = 0
    jump_force = 70
    # jump_force = 100
    jump_force_decrement = 10

    # state
    jumping = False
    direction = States.RIGHT
    movement = [False, False]
    grounded = False
    blocked = False
    sucking = False
    # has_virus = False
    owned_virus: Virus | None = None

    def get_texture(self): return self.animations[self.animation][self.frame]
    def set_animation(self, animation):
        self.animation = animation
        self.frame = -1
        self.frame_hold = -1

class Surface(Box):
    def __init__(self, **args):
        for key, val in args.items(): setattr(self, key, val)
        super().__init__()

# should a virus point to the box it's contained within or should container point to viruses it contains?
class Virus(Box):
    container: Box
    speed = 2
    xy_direction = [1, 1]
    direction = 'north-east'

    def __init__(self, **args):
        for key, val in args.items(): setattr(self, key, val)
        super().__init__(
            color = pygame.Color('yellow'),
            wh = [60, 60],
            xy = [0, 200]
        )

class Game():
    show_console = True
    show_grid = True

class World():
    # physics
    gravity = 8

    mouse_xy = [0, 0]
    input_states = { input: States.DEPRESSED for input in Inputs }
    mapping = {
        Inputs.LEFT: [pygame.K_LEFT, pygame.K_a],
        Inputs.RIGHT: [pygame.K_RIGHT, pygame.K_d],
        Inputs.JUMP: [pygame.K_SPACE],
        Inputs.SUCK: [pygame.K_DOWN, pygame.K_s],

        Inputs.PLACE: [pygame.BUTTON_LEFT],

        Inputs.DEBUG_1: [pygame.K_1],
        Inputs.DEBUG_2: [pygame.K_2],

        Inputs.DEBUG_7: [pygame.K_7],
        Inputs.DEBUG_8: [pygame.K_8],
        Inputs.DEBUG_9: [pygame.K_9],
        Inputs.DEBUG_0: [pygame.K_0],

        Inputs.CAM_LEFT: [pygame.K_j],
        Inputs.CAM_RIGHT: [pygame.K_l],
        Inputs.CAM_DOWN: [pygame.K_k],
        Inputs.CAM_UP: [pygame.K_i],
        # Inputs.CAM_ZOOM_IN: [pygame.BUTTON_WHEELUP, pygame.K_EQUALS],
        # Inputs.CAM_ZOOM_OUT: [pygame.BUTTON_WHEELDOWN, pygame.K_MINUS]
        Inputs.CAM_ZOOM_IN: [pygame.K_EQUALS],
        Inputs.CAM_ZOOM_OUT: [pygame.K_MINUS]
    }

    # game world objects
    boxes = [ ]
    next_box = Box()
    surfaces = [
        Surface(xy=[-200, 200], wh=[100, 100]),
        Surface(xy=[-500, 200], wh=[100, 100]),
        Surface(xy=[200, 350], wh=[100, 100]),
        Surface(xy=[000, 000], wh=[1000, 200]),
        Surface(xy=[800, 200], wh=[200, 200]),
    ]
    # viruses = [ Virus(container=surfaces[3]) ]
    viruses = []

    def __init__(self):
        pass

camera = Camera()
player = Player()
world = World()

data_path = "data/settings.pkl"

def delete_data():
    console_log("Deleting")
    open(data_path, "w").close()

def load_data():
    global game
    if os.path.getsize(data_path) > 0:
        with open('data/settings.pkl', 'rb') as file:
            game = pickle.load(file)
    else:
        game = Game()
        console_log('Not loading data - does not exist')

def save_data():
    console_log('Saving')
    with open(data_path, 'wb') as file:
        pickle.dump(game, file)

load_data()
