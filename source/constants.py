from enum import Enum

States = Enum('States', [
    'LEFT', 'RIGHT',
    'DEPRESSING', 'PRESSING', 'DEPRESSED', 'PRESSED', # key states
])
Animations = Enum('Animations', [
    'NONE', 'WALK', 'TURN', 'JUMP', 'FALL', # animations
])
Inputs = Enum('Inputs', [
    'LEFT', 'RIGHT', 'JUMP', 'SUCK', 'SPIT',
    'PLACE',
    'DEBUG_1', 'DEBUG_2', 'DEBUG_7', 'DEBUG_8', 'DEBUG_9', 'DEBUG_0',
    'CAM_LEFT', 'CAM_RIGHT', 'CAM_DOWN', 'CAM_UP', 'CAM_ZOOM_IN', 'CAM_ZOOM_OUT',
])

pallate = [
    (0, 0, 0),
    (255, 255, 255),
]
