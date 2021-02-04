# Import needed modules
import pygame as py

# Import constants
from classes.constants import *

class button:
    def __init__(self, pos, size, gamesurf, function, *args):
        self.pos = pos
        self.size = size
        self.function = function
        self.args = args
        self.gamesurf = gamesurf

    def draw(self):
        rectangle = py.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        py.draw.rect(self.gamesurf, GREY, rectangle)
