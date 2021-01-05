# Import needed modules
import pygame as py
from classes.constants import *

class projectile:
    def __init__(self, start, dierection, power, weapon, team, gamesurf):
        self.gamesurf = gamesurf
        self.start = start
        self.dierection = dierection
        self.power = int(power)
        self.team = team
        self.weapon = weapon
        self.range = weapon.range

        if self.power != 0:
            if self.weapon.type == physical:
                self.dierection.scale_to_length(self.power*4)
            elif self.weapon.type == laser:
                self.dierection.scale_to_length(self.power*6)
            else:
                self.dierection.scale_to_length(self.power)

        self.offset = self.dierection

    def draw(self, offset):
        newStart = self.start - offset
        newStart = (int(newStart[0]), int(newStart[1]))
        #self.offset.scale_to_length(self.weapon.speed/1000 * time) # TODO

        if self.weapon.type == plasma:
            py.draw.circle(self.gamesurf, self.weapon.color, (int(newStart[0]), int(newStart[1])), int(self.power/2))
        else:
            py.draw.line(self.gamesurf, self.weapon.color, newStart, (newStart + self.dierection), self.power*2)

        self.start += self.offset
        self.range -= self.offset.length()