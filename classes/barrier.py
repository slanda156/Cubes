# Import needed modules
import pygame as py

class barrier:
    def __init__(self, pos, size, death=False):
        self.pos = pos
        self.size = size
        self.death = death

    def draw(self, offset):
        self.newPos = self.pos - offset

        self.newPos = (int(self.newPos[0]), int(self.newPos[1]))

        if self.death:
            py.draw.rect(gamesurf, RED, (self.pos[0], self.pos[1], self.size[0], self.size[1]))
        else:
            py.draw.rect(gamesurf, LIGHTGREY, (self.pos[0], self.pos[1], self.size[0], self.size[1]))