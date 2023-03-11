import pygame as py

from src.config import colors

class iconAndText:
    def __init__(self, sprit, scale, font, textColor, text, pos, gamesurf):
        self.gamesurf = gamesurf
        self.sprit = sprit
        self.scale = scale
        self.font = font
        self.textColor = textColor
        self.text = text
        self.pos = pos

    def draw(self, text=None):
        if text is not None:
            self.text = text

        widget = self.font.render(str(self.text), True, self.textColor)

        if self.sprit is not None:
            self.gamesurf.blit(self.sprit, self.pos)
        self.gamesurf.blit(widget, (self.pos[0]+50, self.pos[1]))

class icon:
    def __init__(self, sprit, pos):
        self.sprit = sprit
        self.pos = pos

    def draw(self):
        self.gamesurf.blit(self.sprit, self.pos)

class button:
    def __init__(self, pos, size, gamesurf, function, *args):
        self.pos = pos
        self.size = size
        self.function = function
        self.args = args
        self.gamesurf = gamesurf

    def draw(self):
        rectangle = py.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        py.draw.rect(self.gamesurf, colors["GREY"], rectangle)
