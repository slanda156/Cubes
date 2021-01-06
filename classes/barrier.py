# Import needed modules
import pygame as py
from classes.constants import *

class barrier:
    def __init__(self, pos, size, death=False):
        self.pos = pos
        self.size = size
        self.death = death

    def draw(self, offset):
        newPos = self.pos - offset

        newPos = (int(self.newPos[0]), int(self.newPos[1]))

        if self.death:
            py.draw.rect(self.gamesurf, RED, (newPos[0], newPos[1], self.size[0], self.size[1]))
        else:
            py.draw.rect(self.gamesurf, LIGHTGREY, (newPos[0], newPos[1], self.size[0], self.size[1]))