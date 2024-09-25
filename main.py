'''
main.py: creates a pygame window and handles the loading of game code dynamically
meaning once a source file is saved the game will restart with new changes
'''

from types import ModuleType
import pygame, importlib, time, os, sys, ctypes
import library

def get_timestamps():
    return [
        os.path.getmtime(f"source/{file}") for file in os.listdir('source')
        if file[-3:] == '.py'
    ]

class DLL:
    module: ModuleType
    module_name = "source.game"
    module_path = "source/game.py"
    module_dir = "source"
    last_modified = get_timestamps()

    errors = False
    errors_msg: str

fps = 60
width, height = 960, 720
pygame.init()
pygame.display.set_caption("Infection")
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
error_img = pygame.transform.scale(pygame.image.load(f'assets/error.png'), (width//2, width//2))
library.init(screen)

def load_dynamic():
    print('Loading game code')
    try:
        if not hasattr(DLL, 'module'):
            DLL.module = importlib.import_module(DLL.module_name)
        else:
            DLL.module.destroy()
            importlib.reload(DLL.module)

        DLL.module.init(screen=screen, width=width, height=height)
        DLL.errors = False
    except Exception as e:
        DLL.errors = True
        tb = e.__traceback__
        DLL.errors_msg = "\n".join([
            f"Initialization Error(s): {e}",
        ])


def check_modified():
    current_check = get_timestamps()
    if (current_check != DLL.last_modified):
        DLL.last_modified = current_check
        return True
    return False

def stop_running():
    pygame.quit()
    sys.exit()

def process_input(events):
    for e in events:
        match e.type:
            case pygame.QUIT: stop_running()
            case pygame.KEYDOWN:
                match e.key:
                    case pygame.K_ESCAPE: stop_running()
                    case pygame.K_r: load_dynamic()

def error_render():
    screen.fill((255, 255, 255))
    library.simple_text(font, pygame.Color('red'), DLL.errors_msg, 10, 10)
    screen.blit(error_img, (width//2, height//2))
    pygame.display.flip()

def main_loop():
    while True:
        if check_modified():
            load_dynamic()
        events = pygame.event.get()
        process_input(events)
        if DLL.errors:
            error_render()
        else:
            try:
                DLL.module.main_loop(events)
            except Exception as e:
                DLL.errors = True
                DLL.errors_msg = f"Runtime error: {e.__traceback__}"
        clock.tick(fps)

load_dynamic()
main_loop()
