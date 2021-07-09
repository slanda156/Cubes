# Import needed modules
import random as ra
import pygame as py
from classes.constants import *
from classes.weapons import *
from classes.functions import findPlayerChar
from classes.armor import armorNum, armors
from classes.character import character

class spawnPoint:
    def __init__(self, pos, team, gamesurf):
        self.gamesurf = gamesurf
        self.pos = pos
        self.team = team
        self.units = []
        self.level = 1
        self.maxCooldown = 7
        self.minCooldown = 4
        self.cooldown = self.maxCooldown

    def draw(self, offset, time):
        self.level += time / 60

        newPos = (self.pos[0] - offset[0], self.pos[1] - offset[1])
        newPos = (int(newPos[0]), int(newPos[1]))

        py.draw.rect(self.gamesurf, GREY, (newPos[0]-30, newPos[1]-30, 60, 60))
        py.draw.rect(self.gamesurf, GREEN, (newPos[0]-25, newPos[1]-25, 50, 50))

    def spawn(self, gamesurf, time, difficulty, characters):
        maxUnits = enemyPower // 5

        if maxUnits <= 0:
            maxUnits = 1

        if self.team != 0 and len(self.units)-1 <= maxUnits:
            if self.cooldown <= 0:
                allowedWeapons = []
                allowedWeaponTypes = []
                if self.level // 1 >= 1:
                    allowedWeaponTypes.append(physical)

                if difficulty // 3 >= 1:
                    allowedWeaponTypes.append(fire)

                if difficulty // 6 >= 1:
                    allowedWeaponTypes.append(plasma)

                if difficulty // 9 >= 1:
                    allowedWeaponTypes.append(laser)

                for a in allowedWeaponTypes:
                    for b in weapons:
                        if b.type == a:
                            allowedWeapons.append(b)

                if len(allowedWeapons) > 1:
                    weaponIn = ra.randrange(0, len(allowedWeapons))
                else:
                    weaponIn = 0
                armorIn = ra.randrange(0, armorNum)

                # Debug info
                logger.debug("Spawning character")

                # Spawning character
                characters.append(character(self.pos, self, self.team, allowedWeapons[weaponIn], armors[armorIn], baseSpeed, 0, gamesurf))

                self.cooldown = ra.randint(self.minCooldown, self.maxCooldown)
            else:
                self.cooldown -= time