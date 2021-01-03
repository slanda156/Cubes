# Import needed modules
import pygame as py

class icon:
    def __init__(self, sprit, pos):
        self.sprit = sprit
        self.pos = pos

    def draw(self):
        gamesurf.blit(self.sprit, self.pos)