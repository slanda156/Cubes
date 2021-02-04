# Import needed modules
import pygame as py

# Import constants
from classes.constants import *

class settingField:
    def __init__(self, pos, size, gamesurf, **args):
        self.pos = pos
        self.size = size
        self.args = args
        self.gamesurf = gamesurf

    def draw(self):
        rectangle = py.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        py.draw.rect(self.gamesurf, LIGHTGREY, rectangle)
        rectangle = py.Rect(self.pos[0]+10, self.pos[1]+10, self.size[0]-20, self.size[1]-20)
        py.draw.rect(self.gamesurf, GREY, rectangle)

    def getValue(self, setting):
        pass
