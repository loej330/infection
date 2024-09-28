'''
# game.py: inits the game's reference to the window & runs the main loop that occurs every frame
'''

import time, pygame, sys

import library
import source.constants
import source.objects

from enum import Enum
from collections import deque
from dataclasses import dataclass

def init(**args):
    source.objects.Window.screen = args['screen']
    source.objects.Window.width = args['width']
    source.objects.Window.height = args['height']
    library.init(source.objects.Window.screen)

# from source import input, render, logic
import source.input
import source.render
import source.logic

def main_loop(events):
    source.input.process_input(events)
    source.logic.update_world()
    source.render.render_items()

def quit():
    source.objects.save_data()

# needed because python does not properly destroy all imports from the context main.py
def destroy():
    if 'source.constants' in sys.modules: del sys.modules['source.constants']
    if 'source.objects' in sys.modules: del sys.modules['source.objects']
    if 'source.input' in sys.modules: del sys.modules['source.input']
    if 'source.render' in sys.modules: del sys.modules['source.render']
    if 'source.logic' in sys.modules: del sys.modules['source.logic']
