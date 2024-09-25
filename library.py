from dataclasses import dataclass
from pygame.surface import Surface

@dataclass
class G:
    screen: Surface
# TODO: better way of indicating what the args actually are when looking at the definition of this function in LSP
def init(*args):
    global g
    g = G(*args)

def simple_text(font, rgb, text, x, y):
    width = 60
    lines = text.split('\n')
    lines = sum([[line[i:i+width] for i in range(0, len(line), width)] for line in lines], [])
    for line in lines:
        g.screen.blit(font.render(line, True, rgb), (x, y))
        y += font.get_linesize()
