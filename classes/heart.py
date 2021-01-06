# Import needed modules
import pygame as py
from classes.light import *
from classes.constants import *

class heart:
    def __init__(self, pos, team, sprit, gamesurf):
        self.gamesurf = gamesurf
        self.pos = pos
        self.team = team
        self.sprit = sprit
        self.maxCooldown = 120
        self.cooldown = self.maxCooldown
        #self.light = light(self.pos, RED, 3, gamesurf)

    def atack(self):
        pass

    def draw(self, offset, time):
        newPos = self.pos - offset
        newPos = (int(newPos[0]), int(newPos[1]))

        # Draw sprit
        self.gamesurf.blit(self.sprit, newPos)

        self.cooldown -= time

        if self.cooldown <= 0:
            self.cooldown = 0