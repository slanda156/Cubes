# Import needed modules
import random as ra
import pygame as py
from classes.heart import *
from classes.spawnpoint import *
from classes.constants import images
from classes.functions import calcDist

class nest:
    def __init__(self, pos, team, gamesurf):
        self.gamesurf = gamesurf
        self.pos = pos
        self.spawns = []
        self.hearts = []
        self.maxSpawns = 7
        self.maxHearts = 1
        self.team = team
        self.spawnChanceHeart = 0.16  # *FPS = %/s
        self.spawnChanceSpawns = 0.5 # *FPS = %/s

    def resize(self):
        if len(self.hearts)-1 < self.maxHearts:
            i = ra.randrange(1, 1001)
            # Check if it should spawn
            if i/10 <= self.spawnChanceHeart:
                # Generate position
                x = ra.randint(-20*self.maxHearts, 20*self.maxHearts)
                y = ra.randint(-20*self.maxHearts, 20*self.maxHearts)
                pos = py.Vector2(x, y)
                pos += self.pos
                # Generate heart
                localheart = heart(pos, self.team, images.get("heart1.png"), self.gamesurf)
                # Add it to the lsist
                self.hearts.append(localheart)

        if len(self.spawns)-1 < self.maxSpawns:
            i = ra.randrange(1, 1001)
            # Check if it should spawn
            if i/10 <= self.spawnChanceSpawns:
                # Generate position
                x = ra.randint(-15*self.maxSpawns, 15*self.maxSpawns)
                y = ra.randint(-15*self.maxSpawns, 15*self.maxSpawns)
                pos = py.Vector2(x, y)
                pos += self.pos
                # Generate spawns
                spawns = spawnPoint(pos, self.team, self.gamesurf)
                # Check distance to other spawns and hearts
                retry = True
                for x in self.spawns:
                    if calcDist(pos, x.pos) <= 80:
                        retry = False

                for x in self.hearts:
                    if calcDist(pos, x.pos) <= 100:
                        retry = False

                if retry:
                    # Add it to the lsist
                    self.spawns.append(spawns)

    def draw(self, offset, waveCooldown, gamesurf, time, difficulty, characters):
        newPos = self.pos - offset
        newPos = (int(newPos[0]), int(newPos[1]))

        # Draw all hearts
        #for x in self.hearts:
            #x.draw(offset)
        # Draw all spawns
        for x in self.spawns:
            x.draw(offset, time)
            if waveCooldown <= 0:
                x.spawn(gamesurf, time, difficulty, characters)