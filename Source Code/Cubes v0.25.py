# Import modules

import math
import sys
import glob
import logging
import time as ti
import traceback
import random as ra
import pygame as py

# Import classes

from damageTypes import damageTypes
from weapons import weaponNum, weapons, initWeapon
from armor import armorNum, armors, initArmor
from item import itemNum, items, initItem
from upgrade import upgradeNum, upgrades, initUpgrade

# Define the window
setFPS = 60
QUALITY = (16, 9)
cordOffset = py.Vector2(0, 0)
WINDOWWIDTH = 2040
WINDOWHEIGHT = int((WINDOWWIDTH/QUALITY[0])*QUALITY[1])

version = "0.24"

# Sets the logging filter
t = ti.localtime()
currentTime = ti.strftime("%H_%M_%S", t)
startTime = ti.time()
logging.basicConfig(filename=f"log_{currentTime}.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

logging.info(f"Starting, version: {version}")

# Define Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTGREY = (169, 169, 169)
GREY = (100, 100, 100)
DARKGREY = (65, 65, 65)
RED = (255, 0, 0)
LIGHTRED = (230, 95, 57)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ERROCOLOR = (255, 0, 102)

# Define Fonts

py.font.init()

buttonFont = py.font.SysFont("Comic Sans Ms", 24)
titleFont = py.font.SysFont("Comic Sans Ms", 35)
title2Font = py.font.SysFont("Comic Sans Ms", 65)
itemFont = py.font.SysFont("Comic Sans Ms", 18)
effectFont = py.font.SysFont("Comic Sans Ms", 18)

# Define Textures
boss = {
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 1, 0, 1, 1, 0, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    0, 0, 1, 1, 1, 1, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
}

# Define Variables

running = True

movement = "none"

levelText = None

characters = []
towers = []
projectiles = []
barriers = []
dots = []
nests = []

downTriangle = [py.Vector2(0, 0), py.Vector2(20, 0), py.Vector2(10, 10)]
upTriangle = [py.Vector2(0, 10), py.Vector2(20, 10), py.Vector2(10, 0)]

hudMode = 0
waveCooldown = 0
oldLevel = 0
maxChar = 0
time = 0
weaponIndex = 0
armorIndex = 0
baseSpeed = 150 # pixel/s
towerBaseCost = 10

# Weapon Types

electric = damageTypes.get("electric")
fire = damageTypes.get("fire")
physical = damageTypes.get("physical")
laser = damageTypes.get("laser")
plasma = damageTypes.get("plasma")

# Define Classes

class point:
    def __init__(self, pos):
        self.pos = pos

    def draw(self, offset):
        self.newPos = self.pos - offset

        self.newPos = (int(self.newPos[0]), int(self.newPos[1]))

        py.draw.circle(gamesurf, ERROCOLOR, self.newPos, 10)

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

class nest:
    def __init__(self, pos, team):
        self.pos = pos
        self.members = []
        self.hearts = []
        self.maxVal = 7
        self.team = team
    
    def append(self, member):
        self.members.append(member)
        self.size = len(self.members)

        if self.size >= self.maxVal:
            self.maxVal += 2
            i = 0
            a = ra.randrange(0, self.size - 1)
            
            while i < 2:
                del self.members[a]
                self.size = len(self.members)
                i += 1
            
            self.hearts.append(heart(self.pos, self.team))

    def attack(self):
        for x in self.hearts:
            if x.cooldown <= 0:
                x.attack()

    def draw(self, offset):
        self.newPos = self.pos - offset
        self.newPos = (int(self.newPos[0]), int(self.newPos[1]))
        pass

class heart:
    def __init__(self, pos, team):
        self.pos = pos
        self.team = team
        self.maxCooldown = 120
        self.cooldown = self.maxCooldown
        self.dot = point(self.pos)

    def atack(self):
        pass

    def draw(offset):
        self.newPos = self.pos - offset
        self.newPos = (int(self.newPos[0]), int(self.newPos[1]))

        self.cooldown -= time

        if self.cooldown <= 0:
            self.cooldown = 0

        self.dot.draw(offset)

class spawnPoint:
    def __init__(self, pos, team):
        self.pos = pos
        self.team = team
        self.maxCooldown = 7
        self.minCooldown = 4
        self.cooldown = self.maxCooldown

    def draw(self, offset):
        self.newPos = (int(self.pos[0] - offset[0]), int(self.pos[1] - offset[1]))
        

        py.draw.rect(gamesurf, GREY, (self.newPos[0]-30, self.newPos[1]-30, 60, 60))
        py.draw.rect(gamesurf, GREEN, (self.newPos[0]-25, self.newPos[1]-25, 50, 50))

    def spawn(self):
        if self.team != 0 and len(characters) < maxChar + 1:
            if self.cooldown <= 0:
                allowedWeapons = []
                allowedWeaponTypes = []
                if characters[findPlayerChar()].level // 1 >= 1:
                    allowedWeaponTypes.append(physical)

                if characters[findPlayerChar()].level // 3 >= 1:
                    allowedWeaponTypes.append(fire)

                if characters[findPlayerChar()].level // 6 >= 1:
                    allowedWeaponTypes.append(plasma)

                if characters[findPlayerChar()].level // 9 >= 1:
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
                logging.info("Spawning character")

                # Spawning character
                characters.append(character(self.pos, self, self.team, allowedWeapons[weaponIn], armors[armorIn], baseSpeed))

                self.cooldown = ra.randint(self.minCooldown, self.maxCooldown)
            else:
                self.cooldown -= time

class projectile:
    def __init__(self, start, dierection, power, weapon, team):
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
        self.newStart = self.start - offset
        self.newStart = (int(self.newStart[0]), int(self.newStart[1]))
        #self.offset.scale_to_length(self.weapon.speed/1000 * time) # FIX

        if self.weapon.type == plasma:
            py.draw.circle(gamesurf, self.weapon.color, (int(self.newStart[0]), int(self.newStart[1])), int(self.power/2))
        else:
            py.draw.line(gamesurf, self.weapon.color, self.newStart, (self.newStart + self.dierection), self.power*2)

        self.start += self.offset
        self.range -= self.offset.length()

class effect:
    def __init__(self, effectType, effectDuration, effectDamage, effectColor):
        self.type = effectType
        self.duration = effectDuration
        self.damage = effectDamage
        self.color = effectColor

class tower:
    def __init__(self, pos, team, weapon, level, accuracy):
        self.team = team
        self.type = "tower"
        self.weapon = weapon
        self.level = level
        self.maxHealth = self.level * 5
        self.health = self.maxHealth
        self.maxCooldown = weapon.reloadTime / 100
        self.cooldown = self.maxCooldown
        self.accuracy = accuracy
        self.radius = 15
        self.factor = 1.2
        self.effect = []
        self.pos = (int(pos[0]+(self.radius*self.factor)), int(pos[1]+(self.radius*self.factor)))
        self.size = (self.radius * 2 * self.factor, self.radius * 2 * self.factor)

    def draw(self, offset):
        self.newPos = self.pos - offset

        self.newPos = (int(self.newPos[0]), int(self.newPos[1]))

        for x in self.effect:
            self.health -= x.damage
            
            if x.duration <= 0:
                try:
                    del self.effect[self.effect.index(x)]
                    logging.info("Removing effect")
                except:
                    logging.warning("Effect not deletet")

        self.target = py.mouse.get_pos() - offset

        if getNearestEnemieChar(self) is not None:
            self.target = getNearestEnemieChar(self).pos

        if not checkList(self.effect, "shocked"):
            self.dir = py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1])
            self.dir.scale_to_length(int(self.radius*(self.factor+0.2)))

        if self.cooldown <= 0:
            if calcDist(self.pos, self.target) <= self.weapon.range:
                self.shoot(self.target)

        if self.cooldown > 0:
            self.cooldown -= time

        py.draw.rect(gamesurf, GREY, ((self.newPos[0]-(self.size[0]/2)), (self.newPos[1]-(self.size[1]/2)), self.size[0], self.size[1]))

        py.draw.circle(gamesurf, RED, self.newPos, self.radius)

        py.draw.line(gamesurf, self.weapon.color, self.newPos, (self.newPos + self.dir), int(self.radius/4))

    def getHit(self, weapon):
        self.effectDuration = weapon.effectDuration

        if weapon.effect is not None:
            self.effect.append(effect(weapon.effect, weapon.effectDuration, weapon.effectDamage, weapon.color))

        self.health -= weapon.damage

    def shoot(self, target):
        appendProjectiles(self.pos, py.Vector2(target[0]-self.pos[0], target[1]-self.pos[1]), self.weapon.power, self.weapon, self.team, self.accuracy)

        self.cooldown = self.maxCooldown

    def healthBar(self):
        pos = self.newPos + py.Vector2(0, -20)

        py.draw.rect(gamesurf, GREY, (pos[0]-20, pos[1]-6, 40, 12))

        py.draw.rect(gamesurf, LIGHTGREY, (pos[0]-18, pos[1]-4, 36, 8))

        i = self.health / self.maxHealth

        py.draw.rect(gamesurf, RED, (pos[0]-18, pos[1]-4, int(36*i), 8))

class character:
    def __init__(self, pos, origine, team, weapon, armor, speed, controlled=False):
        self.controlled = controlled
        self.pos = [pos[0], pos[1]]
        self.origine = origine
        self.team = team
        self.type = "player"
        self.weapon = weapon
        self.armor = armor
        self.cooldown = 0.1
        self.maxCooldown = self.weapon.reloadTime / 100
        self.target = [0, 0]
        self.level = 1
        self.xp = 0
        self.resources = 0
        self.upgrades = []
        self.maxCharge = 200
        self.charge = 0
        self.towerCost = towerBaseCost
        self.towerUpgrades = []
        self.towerAccuracy = 1
        self.towerWeapon = weapons[findObjectInList(weapons, "rifle")]
        self.accuracy = 1
        self.inventory = {items[0].name: items[0]}

        if self.armor.type == physical:
            self.maxHealth = float(10 * self.level * 2)
        else:
            self.maxHealth = float(10 * self.level)

        self.health = self.maxHealth
        self.maxBoost = 100
        self.boost = self.maxBoost
        self.effect = []
        self.effectDuration = 0
        self.effectDamage = 0
        self.radius = 20

        if self.armor.type == physical:
            self.movementSpeed = int(speed * 0.8)
        else:
            self.movementSpeed = int(speed)

    def draw(self, offset):
        self.newPos = self.pos - offset
        self.newPos = (int(self.newPos[0]), int(self.newPos[1]))

        self.maxCooldown = self.weapon.reloadTime / 100

        if self.armor.type == physical:
            self.maxHealth = float(10 * self.level * 2)
        else:
            self.maxHealth = float(10 * self.level)

        if self.boost > self.maxBoost:
            self.boost = self.maxBoost
        else:
            self.boost = self.maxBoost

        if self.charge < self.maxCharge:
            self.charge += time*10
        else:
            self.charge = self.maxCharge

        if self.xp >= (self.level * 100):
            self.xp = 0
            self.level += 1

        for x in self.effect:
            if x.type == self.armor.type:
                self.health -= (x.damage*time)/2
            else:
                self.health -= x.damage*time

            if x.duration <= 0:
                try:
                    del self.effect[self.effect.index(x)]
                except:
                    logging.warning("Effect not deletet")

        if self.controlled:
            self.target = py.mouse.get_pos() + offset

        elif calcDist(self.pos, characters[findPlayerChar()].pos) <= 1500:
            self.target = characters[findPlayerChar()].pos

            if not self.controlled:
                self.dir = py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1])
                self.ai()

        else:
            self.idle()
        
        self.dir = py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1])
        try:
            self.dir.scale_to_length(30)
        except:
            logging.warning("Cannot scale a vector with zero length")

        for x in self.effect:
            if x.duration > 0:
                x.duration -= time

        py.draw.circle(gamesurf, (200, 200, 200), (int(self.newPos[0]), int(self.newPos[1])), self.radius)

        py.draw.line(gamesurf, self.weapon.color, self.newPos, (self.newPos + self.dir), int(self.radius/4))

        py.draw.circle(gamesurf, self.armor.color, (int(self.newPos[0]), int(self.newPos[1])), int(self.radius/3))

        self.cooldown -= time

    def idle(self):
        # Check how far away the origine is
        if calcDist(self.pos, self.origine.pos) >= 250:
            # Set origine as target
            self.target = self.origine.pos

        elif calcDist(self.pos ,self.target) < 250:
            # Get x & y cordinates
            a = self.pos[0]
            b = self.pos[1]
            # Generate vector out of position
            target = py.Vector2(a, b)
            # Rotate vector
            target = target.rotate(1)

        # Generate direction to move
        self.dir = py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1])

        self.dir.scale_to_length(int(self.movementSpeed * time))

        if not checkList(self.effect, "shocked"):
            if calcDist(self.pos, self.target) > (self.weapon.range/2):
                if self.boost > 0 and calcDist(self.pos, self.target) > self.weapon.range:
                    self.dir.scale_to_length(int((self.movementSpeed * 2) * time))
                    self.boost -= 20
                else:
                    self.boost += 10

                self.pos[0] += int(self.dir[0])
                self.pos[1] += int(self.dir[1])

            else:
                if self.boost > 0 and calcDist(self.pos, self.target) < (self.weapon.range/3):
                    self.dir.scale_to_length(int((self.movementSpeed * 2) * time))
                    self.boost -= 20
                else:
                    self.boost += 10

                self.pos[0] -= int(self.dir[0])
                self.pos[1] -= int(self.dir[1])

    def ai(self):
        if not checkList(self.effect, "shocked"):
            if self.cooldown <= 0:
                if calcDist(self.pos, self.target) < self.weapon.range:
                    self.shoot()

            self.dir.scale_to_length(int(self.movementSpeed * time))

            if calcDist(self.pos, self.target) > (self.weapon.range/2):
                if self.boost > 0 and calcDist(self.pos, self.target) > self.weapon.range:
                    self.dir.scale_to_length(int((self.movementSpeed * 2) * time))
                    self.boost -= 20
                else:
                    self.boost += 10

                self.pos[0] += int(self.dir[0])
                self.pos[1] += int(self.dir[1])

            else:
                if self.boost > 0 and calcDist(self.pos, self.target) < (self.weapon.range/3):
                    self.dir.scale_to_length(int((self.movementSpeed * 2) * time))
                    self.boost -= 20
                else:
                    self.boost += 10

                self.pos[0] -= int(self.dir[0])
                self.pos[1] -= int(self.dir[1])

    def getHit(self, weapon):
        self.effectDuration = weapon.effectDuration

        if weapon.effect is not None:
            if checkList(self.effect, weapon.effect):
                effectPos = self.effect.index(weapon.effect)
                self.effect[effectPos].effectDuration = weapon.effectDuration
                self.effect[effectPos].effectDamage = weapon.effectDamage

            else:
                self.effect.append(effect(weapon.type, weapon.effectDuration, weapon.damage/10, weapon.color))

        if self.armor.type == weapon.type:
            self.health -= weapon.damage/2

        else:
            self.health -= weapon.damage

    def healthBar(self):
        pos = self.newPos + py.Vector2(0, -20)

        py.draw.rect(gamesurf, GREY, (pos[0]-20, pos[1]-6, 40, 12))

        py.draw.rect(gamesurf, LIGHTGREY, (pos[0]-18, pos[1]-4, 36, 8))

        i = self.health / self.maxHealth

        if i > 1:
            i = 1

        py.draw.rect(gamesurf, RED, (pos[0]-18, pos[1]-4, int(36*i), 8))

    def shoot(self):
        appendProjectiles(self.pos, py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1]), self.weapon.power, self.weapon, self.team, self.accuracy)

        self.cooldown = self.maxCooldown

class textWidget:
    def __init__(self, font, color, pos, surface):
        self.font = font
        self.color = color
        self.pos = pos
        self.surface = surface

    def draw(self, text):
        widget = self.font.render(str(text), True, self.color)

        self.surface.blit(widget, self.pos)

class icon:
    def __init__(self, sprit, pos, surface):
        self.sprit = sprit
        self.pos = pos
        self.surface = surface

    def draw(self):
        py.Surface.blit(self.sprit, self.pos)

class iconAndText:
    def __init__(self, sprit, scale, font, textColor, text, pos, surface):
        self.sprit = sprit
        self.scale = scale
        self.font = font
        self.textColor = textColor
        self.text = text
        self.pos = pos
        self.surface = surface

    def draw(self, text=None):
        if text is not None:
            self.text = text

        widget = self.font.render(str(self.text), True, self.textColor)

        if self.sprit is not None:
            py.Surface.blit(self.sprit, self.pos)
        self.surface.blit(widget, (self.pos[0]+50, self.pos[1]))

# Declare Functions

def findPlayerChar():
    for x in characters:
        if x.controlled:
            return characters.index(x)

def checkCollision(character, object):
    hyp = 0
    offset = py.Vector2(y.pos[0]+y.size[0]/2, y.pos[1]+y.size[1]/2)
    vector = py.Vector2(character.pos[0]-offset[0], character.pos[1]-offset[1])
    if vector[0] > 0 and vector[1] < 0:
        x = (0*90) + math.degrees(math.atan(positiveNum(vector[0])/positiveNum(vector[1])))
        if x <= 45:
            hyp = (object.size[1]/2)/math.cos(math.radians(x))
        elif x > 45:
            hyp = (object.size[0]/2)/math.cos(math.radians(x))

    elif vector[0] > 0 and vector[1] > 0:
        x = math.degrees(math.atan(positiveNum(vector[1])/positiveNum(vector[0])))
        if x <= 45:
            hyp = (object.size[1]/2)/math.cos(math.radians(x))
        elif x > 45:
            hyp = (object.size[0]/2)/math.cos(math.radians(x))

    elif vector[0] < 0 and vector[1] > 0:
        x = math.degrees(math.atan(positiveNum(vector[0])/positiveNum(vector[1])))
        if x <= 45:
            hyp = (object.size[1]/2)/math.cos(math.radians(x))
        elif x > 45:
            hyp = (object.size[0]/2)/math.cos(math.radians(x))

    elif vector[0] < 0 and vector[1] < 0:
        x = math.degrees(math.atan(positiveNum(vector[1])/positiveNum(vector[0])))
        if x <= 45:
            hyp = (object.size[1]/2)/math.cos(math.radians(x))
        elif x > 45:
            hyp = (object.size[0]/2)/math.cos(math.radians(x))

    elif vector[0] == 0 and vector[1] < 0:
        hyp = object.size[1]/2

    elif vector[0] > 0 and vector[1] == 0:
        hyp = object.size[0]/2

    elif vector[0] == 0 and vector[1] > 0:
        hyp = object.size[1]/2

    elif vector[0] < 0 and vector[1] == 0:
        hyp = object.size[0]/2

    if hyp + character.radius > vector.length():
        vector.scale_to_length(hyp + character.radius)
        characters[character.seq].pos += vector

def checkCircle(circle, projectile, radius):
    if calcDist(circle.pos, projectile.start) <= radius:
        return True
    else:
        return False

def checkRectangle(rectangle, projectile):
    rect = py.Rect(rectangle.pos[0], rectangle.pos[1], rectangle.size[0], rectangle.size[1])

    if rect.collidepoint(projectile.start + projectile.offset):
        return True
    else:
        return False

def checkList(list, var):
    for x in list:
        if x.type == var:
            return True
        else:
            return False

def findObjectInList(list, var):
    if len(list) <= 1:
        return 0

    else:
        for i in range(len(list)-1):
            if list[i].name == var:
                return i

def checkHits(projectiles, objects):
    for x in projectiles:
        for y in objects:
            if x.team != y.team:
                if y.type == "tower" and checkRectangle(py.Rect(y.pos[0], y.pos[1], y.size[0], y.size[1]), x):
                    y.getHit(x.weapon)
                elif y.type == "player" and checkCircle(y, x, y.radius):
                    y.getHit(x.weapon)
                    if y.health <= 0:
                        if x.team == 0:
                            i = findPlayerChar()
                            characters[i].xp += (characters[i].level*20)        #FIX
                            characters[i].resources += ((y.level/3)*20)

                    try:
                        del projectiles[projectiles.index(x)]
                    except:
                        logging.warning("Projectile not deletet")

def offsetTrajectory(start, splatter):
    start[0] = int(start[0])
    start[1] = int(start[1])

    return py.Vector2(ra.randint(start[0]-splatter, start[0]+splatter), ra.randint(start[1]-splatter, start[1]+splatter))

def appendProjectiles(start, dierection, power, weapon, team, accuracy):
    if weapon.type == fire:
        i = ra.randrange(3, 5)

        while i <= 5:
            newDierection = dierection + offsetTrajectory(dierection, 100 * accuracy)
            projectiles.append(projectile(start, newDierection, power, weapon, team))
            i += 1

    elif weapon.type == electric:
        dierection += offsetTrajectory(dierection, 20 * accuracy)
        projectiles.append(projectile(start, dierection, power, weapon, team))

    elif weapon.type == physical:
        dierection += offsetTrajectory(dierection, 5 * accuracy)
        projectiles.append(projectile(start, dierection, power, weapon, team))

    elif weapon.type == laser:
        dierection += offsetTrajectory(dierection, 2 * accuracy)
        projectiles.append(projectile(start, dierection, power, weapon, team))

    elif weapon.type == plasma:
        dierection += offsetTrajectory(dierection, 20 * accuracy)
        projectiles.append(projectile(start, dierection, power, weapon, team))

def appendTower(pos, team, weapon, level, accuracy):
    characters[findPlayerChar()].resources -= characters[findPlayerChar()].towerCost
    characters[findPlayerChar()].towerCost += towerBaseCost

    towers.append(tower((pos[0], pos[1]-40), team, weapon, level, accuracy))

def calcDist(pos1, pos2):
    distance = py.Vector2(pos2[0]-pos1[0], pos2[1]-pos1[1])

    return distance.length()

def positiveNum(number):
    if number < 0:
        number -= number*2

    return number

def sculpt(pos, texture, color1, color2, color3, scale):
    pass

def getNearestChar(start):
    distance = []
    minDist = [0, 0]
    if len(characters) > 1:
        for x in characters:
            distance.append((calcDist(start.pos, x.pos), characters.index(x)))

        for y in distance:
            if minDist[0] == 0:
                minDist = y

            elif minDist[0] > y[0]:
                minDist = y

        return characters[minDist[1]]

def getNearestFriendlyChar(start):
    distance = []
    minDist = None

    if len(characters) > 1:
        for x in characters:
            if start.team == x.team:
                distance.append((calcDist(start.pos, x.pos), characters.index(x)))

        for y in distance:
            if minDist is None:
                minDist = y

            elif minDist[0] > y[0]:
                minDist = y

        return characters[minDist[1]]

def getNearestEnemieChar(start):
    distance = []
    minDist = [0, 0]

    if len(characters) > 1:
        for x in characters:
            if start.team != x.team:
                distance.append((calcDist(start.pos, x.pos), characters.index(x)))

        for y in distance:
            if minDist[0] <= 0:
                minDist = y

            elif minDist[0] > y[0]:
                minDist = y

        return characters[minDist[1]]

def mindTransport(start, target):
    if start is not None and target is not None:
        oldChar = target
        characters[characters.index(target)] = start
        characters[characters.index(start)] = oldChar

def die():
    global playing
    global dead

    dead = True
    reset()

def generatePointsAroundDot(pos, minVar, maxVar):
    points = []
    power = ra.randrange(minVar, maxVar)
    
    while len(points) < power:
        distance = []
        minVal = 0
    
        a = ra.randrange(-10, 10)
        b = ra.randrange(-10, 10)
        c = ra.randrange(40, 400)
        offset = py.Vector2(a, b)
        
        if offset.length() != 0:
            offset.scale_to_length(c)
    
        if len(points) > 1:
            for x in points:
                if calcDist(x.pos, pos+offset) > 100:
                    distance.append((calcDist(x.pos, pos+offset)))
                
            for x in distance:
                if minVal != 0:
                    if minVal < x:
                        minVal = x
                
                else:
                    minVal = x
    
            if minVal > 50:
                points.append(point(pos+offset))
                
        else:
            points.append(point(pos+offset))
    
    return points

def reset():
    logging.info("Reset")

    gamesurf.fill(BLACK)
    py.event.clear()

    global levelText
    global barriers
    global characters
    global nests
    global projectiles
    global baseSpeed
    global towers
    global cordOffset

    cordOffset[0] = 0
    cordOffset[1] = 0

    oldWeapon = weapons[0]
    oldArmor = armors[0]

    if len(characters) > 0:
        oldWeapon = characters[findPlayerChar()].weapon
        oldArmor = characters[findPlayerChar()].armor

    characters = []
    projectiles = []
    barriers = []
    nests = []
    towers = []

    pos = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
    characters.append(character(pos, None, 0, oldWeapon, oldArmor, baseSpeed, True))

    pos = (ra.randrange(0, WINDOWWIDTH), ra.randrange(0, WINDOWHEIGHT))
    team = 1
    nests.append(nest(pos, team))    

    for x in generatePointsAroundDot(pos, 2, 10):
        nests[0].append(spawnPoint(x.pos, team))

# Initialsation

# Init pygame
if not py.get_init():
    py.init()

# Sets the display
gamesurf = py.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), py.RESIZABLE)
py.display.set_caption(f"Cubes v.{version}")

# Sets screen mode
screen = "main_menu"

# Creates the main clock
clock = py.time.Clock()

# Init all needed modules
initArmor()
initWeapon()
initItem()
initUpgrade()

# Load up sprits
imageNames = glob.glob("images\\*.png")
images =  {}

for x in imageNames:
    x = x.split("\\")[1]
    images[x] = (py.image.load(f"images\\{x}"))

# Main Loop

# Resets all variables
reset()

logging.info(f"Loaded after: {round(ti.time()-startTime, 3)} s")

try:
    while running:
        # Resets backround
        gamesurf.fill(BLACK)
        # Sets global time variable
        time = (clock.get_time() / 1000)
        # Sets log time
        t = ti.localtime()
        currentTime = ti.strftime("%H_%M_%S", t)
        # Gets player charakter
        char = findPlayerChar()

        # Defines the maximum amount of enemies
        if characters[char].level <= 10:
            maxChar = characters[char].level
        else:
            maxChar = 10

        # Define widgets size & position
        resetButtonSize = (150, 40)
        resetButtonPos = ((WINDOWWIDTH//2)-(resetButtonSize[0]//2), (WINDOWHEIGHT//2)-(resetButtonSize[1]//2))

        menuButtonSize = (150, 40)
        menuButtonPos = ((WINDOWWIDTH//2)-(menuButtonSize[0]//2), (WINDOWHEIGHT//2)-menuButtonSize[1]//2+50)

        upPos1 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4)+130)
        downPos1 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4)+80)
        upPos2 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4)+50)
        downPos2 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4))

        # Define widgets
        armorText = textWidget(buttonFont, armors[0].color, ((WINDOWWIDTH/2)-70, (WINDOWHEIGHT/4)+15), gamesurf)
        weaponText = textWidget(buttonFont, weapons[0].color, ((WINDOWWIDTH/2)-70, (WINDOWHEIGHT/4)+90), gamesurf)
        quitText = textWidget(buttonFont, BLACK, ((WINDOWWIDTH/2)-35, (WINDOWHEIGHT/3)+100), gamesurf)
        titletext = textWidget(title2Font, (220, 220, 220), (WINDOWWIDTH/2-90, 150), gamesurf)
        deadText = textWidget(titleFont, RED, (WINDOWWIDTH/2-100, WINDOWHEIGHT*0.2), gamesurf)
        playText = textWidget(buttonFont, BLACK, ((WINDOWWIDTH/2)-30, (WINDOWHEIGHT/3)+50), gamesurf)
        menuText = textWidget(buttonFont, BLACK, (menuButtonPos[0]+(menuButtonSize[0]*0.1), menuButtonPos[1]), gamesurf)
        resetText = textWidget(buttonFont, BLACK, (resetButtonPos[0]+(resetButtonSize[0]*0.22), resetButtonPos[1]), gamesurf)
        pauseText = textWidget(titleFont, WHITE, (WINDOWWIDTH/2-100, WINDOWHEIGHT*0.2), gamesurf)
        fpsText = textWidget(buttonFont, GREEN, ((WINDOWWIDTH/2), 20), gamesurf)
        xpText = textWidget(buttonFont, GREEN, (20, 80), gamesurf)
        levelText = textWidget(buttonFont, GREEN, (20, 50), gamesurf)
        healthText = textWidget(buttonFont, LIGHTRED, (20, 20), gamesurf)
        resourcesText = textWidget(buttonFont, GREEN, ((WINDOWWIDTH-200), 20), gamesurf)
        waveCooldownText = textWidget(titleFont, GREEN, (WINDOWWIDTH/2, 20), gamesurf)

        effectIconText = iconAndText(None, 5, effectFont, ERROCOLOR, "None", (40, WINDOWHEIGHT-80), gamesurf)
        equippedItemIconText = iconAndText(None, 2, itemFont, GREEN, "None", (WINDOWWIDTH-180, 80), gamesurf)

        # Main event loop
        for event in py.event.get():
            # Resize the main window
            if event.type == py.VIDEORESIZE:
                # Resize display
                gamesurf = py.display.set_mode((event.w, event.h), py.RESIZABLE)
                # Gets window size
                WINDOWHEIGHT = gamesurf.get_height()
                WINDOWWIDTH = gamesurf.get_width()

            # Breaks loop when window closes
            if event.type == py.QUIT:
                running = False

            if screen == "main_menu":
                
                # Check for left clicks
                if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                    # Start
                    if playRect.collidepoint(py.mouse.get_pos()):
                        screen = "game_running"
                        reset()

                    # Next weapon
                    elif upWeaponButtonRect.collidepoint(py.mouse.get_pos()):
                        weaponIndex += 1

                    # Last weapon
                    elif downWeaponButtonRect.collidepoint(py.mouse.get_pos()):
                        weaponIndex -= 1

                    # Next armor
                    elif upArmorButtonRect.collidepoint(py.mouse.get_pos()):
                        armorIndex += 1

                    # Last armor
                    elif downArmorButtonRect.collidepoint(py.mouse.get_pos()):
                        armorIndex -= 1

                    # Quit game
                    elif quitButton.collidepoint(py.mouse.get_pos()):
                        running = False

            elif screen == "options":
                pass
            
            elif screen == "game_running":

                # Changing pause status
                if event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE:
                        screen = "game_paused"

                    # Transport mind to nearest enemie
                    elif event.key == py.K_SPACE:
                        if mindTransport(characters[char], getNearestChar(characters[char])) is not None:
                            mindTransport(characters[char], getNearestChar(characters[char]))

                    # Skip wave cooldwon
                    elif event.key == py.K_t and waveCooldown != 0:
                        waveCooldown = 0
                        oldLevel = characters[char].level

                    # Placing Tower
                    elif event.key == py.K_f and characters[char].resources >= characters[char].towerCost:
                        appendTower(characters[char].pos, characters[char].team, characters[char].towerWeapon, characters[char].level, characters[char].towerAccuracy)

                    # TEMP Using equiped item
                    elif event.key == py.K_e and characters[char].resources >= items[findObjectInList(items, "medKit")].cost:
                        characters[char].health += (items[findObjectInList(items, "medKit")].healing/100)*characters[char].maxHealth

                        if characters[char].health > characters[char].maxHealth:
                            characters[char].health = characters[char].maxHealth

                    # Change hud mode
                    elif event.key == py.K_F1:
                        if hudMode == 1:
                            hudMode = 0
                        else:
                            hudMode = 1
                        
                elif event.type == py.MOUSEBUTTONDOWN:
                    # Teleport to mouse position and sets effect
                    if event.button == 3 and characters[char].charge >= 100:
                        characters[char].pos[0] = py.mouse.get_pos()[0] - cordOffset[0]
                        characters[char].pos[1] = py.mouse.get_pos()[1] - cordOffset[1]

                        characters[char].effect.append(effect("shocked", 1.5, 0, (64, 56, 201)))
                        characters[char].effectDuration = 2.5

            elif screen == "game_paused" or screen == "death_screen":

                # Check for button clicks
                if event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE and screen == "game_paused":
                        screen = "game_running"

                elif event.type == py.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if resetButton.collidepoint(py.mouse.get_pos()):
                            reset()
                            screen = "game_running"

                        elif menuButton.collidepoint(py.mouse.get_pos()):
                            screen = "main_menu"

            elif screen == "game_inventory":
                pass


        if screen == "main_menu":
                
            # Draw text & icons
            titletext.draw("Cubes")

            py.draw.rect(gamesurf, GREY, ((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+50, 180, 40))
            playRect = py.Rect((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+50, 180, 40)

            playText.draw("PLAY")

            py.draw.polygon(gamesurf, BLUE, (downTriangle[0]+upPos1, downTriangle[1]+upPos1, downTriangle[2]+upPos1))
            upWeaponButtonRect = py.Rect(upPos1[0], upPos1[1], 20, 20)

            py.draw.polygon(gamesurf, BLUE, (upTriangle[0]+downPos1, upTriangle[1]+downPos1, upTriangle[2]+downPos1))
            downWeaponButtonRect = py.Rect(downPos1[0], downPos1[1], 20, 20)

            py.draw.polygon(gamesurf, BLUE, (downTriangle[0]+upPos2, downTriangle[1]+upPos2, downTriangle[2]+upPos2))
            upArmorButtonRect = py.Rect(upPos2[0], upPos2[1], 20, 20)

            py.draw.polygon(gamesurf, BLUE, (upTriangle[0]+downPos2, upTriangle[1]+downPos2, upTriangle[2]+downPos2))
            downArmorButtonRect = py.Rect(downPos2[0], downPos2[1], 20, 20)

            py.draw.rect(gamesurf, RED, ((WINDOWWIDTH/2)-40, (WINDOWHEIGHT/3)+100, 80, 40))
            quitButton = py.Rect((WINDOWWIDTH/2)-40, (WINDOWHEIGHT/3)+100, 80, 40)

            quitText.draw("QUIT")

            # Handeling weapon & armor selection
            if weaponIndex < 0:
                weaponIndex = weaponNum-1

            elif weaponIndex > (weaponNum-1):
                weaponIndex = 0

            if armorIndex < 0:
                armorIndex = armorNum-1

            elif armorIndex > (armorNum-1):
                armorIndex = 0

            # Draw weapon & armor selection
            weaponText.color = weapons[weaponIndex].color
            armorText.color = armors[armorIndex].color

            weaponText.draw(weapons[weaponIndex].displayName)
            armorText.draw(armors[armorIndex].displayName)

            characters[char].weapon = weapons[weaponIndex]
            characters[char].armor = armors[armorIndex]                   

        elif screen == "options":
            pass
            
        elif screen == "game_running":

            # Getting pressed mouse buttons
            mouse = py.mouse.get_pressed()

            # Handel player shooting
            if mouse[0] == 1 and not checkList(characters[char].effect, "shocked") and characters[char].cooldown <= 0:
                characters[char].shoot()

            # Getting pressed keys
            keys = py.key.get_pressed()

            # Handeling player movment
            if not checkList(characters[char].effect, "shocked"):
                if keys[py.K_w]:
                    if keys[py.K_LSHIFT] and characters[char].boost > 0:
                        characters[char].pos[1] -= characters[char].movementSpeed * 2 * time
                        characters[char].boost -= 10

                    else:
                        characters[char].pos[1] -= characters[char].movementSpeed * time
                        characters[char].boost += 10

                if keys[py.K_s]:
                    if keys[py.K_LSHIFT] and characters[char].boost > 0:
                        characters[char].pos[1] += characters[char].movementSpeed * 2 * time
                        characters[char].boost -= 10

                    else:
                        characters[char].pos[1] += characters[char].movementSpeed * time
                        characters[char].boost += 10

                if keys[py.K_d]:
                    if keys[py.K_LSHIFT] and characters[char].boost > 0:
                        characters[char].pos[0] += characters[char].movementSpeed * 2 * time
                        characters[char].boost -= 10

                    else:
                        characters[char].pos[char] += characters[char].movementSpeed * time
                        characters[char].boost += 10

                if keys[py.K_a]:
                    if keys[py.K_LSHIFT] and characters[char].boost > 0:
                        characters[char].pos[0] -= characters[char].movementSpeed * 2 * time
                        characters[char].boost -= 10

                    else:
                        characters[char].pos[0] -= characters[char].movementSpeed * time
                        characters[char].boost += 10

            # Handels wave cooldown
            if oldLevel != characters[char].level:
                if (characters[char].level % 10) == 0 and waveCooldown <= 0:
                    waveCooldown = 30
                    oldLevel = characters[char].level

            # Delete all enemie characters
            if waveCooldown > 0:
                for x in characters:
                    if x.team != 0:
                        try:
                            del characters[characters.index(x)]
                            logging.info("Removing character")
                        except:
                            logging.warning("Character not deletet")

                # Print remaining time
                waveCooldownText.draw(round(waveCooldown, 1))
                waveCooldown -= time

            #cheking for hits
            #for x in characters:
            #   for y in barriers:
            #       checkCollision(x, y)

            checkHits(projectiles, characters)

            for x in projectiles:
                for y in barriers:
                    if checkRectangle(y, x):
                        try:
                            del projectiles[projectiles.index(x)]
                        except:
                            logging.warning("Projectile not deletet")

            # Check for dead characters and delets them
            for x in characters:
                if x.health <= 0:
                    if x.team == 0:
                        die()

                    else:
                        try:
                            del characters[characters.index(x)]
                            logging.info("Removing character")
                        except:
                            logging.warning("Character not deletet")

            # Draws all objects and handels object specific funktions
            for x in nests:
                x.draw(cordOffset)
                x.attack()

                for y in x.members:
                    y.draw(cordOffset)

                    if waveCooldown <= 0:
                        y.spawn()

            for x in barriers:
                x.draw(cordOffset)

            for x in towers:
                x.draw(cordOffset)

            for x in characters:
                x.draw(cordOffset)
                if x.controlled:
                    # Change cord offset to move window
                    if x.newPos[0] < 500:
                        cordOffset[0] -= (500 - x.newPos[0])
                    if x.newPos[0] > (WINDOWWIDTH - 500):
                        cordOffset[0] += (x.newPos[0] - (WINDOWWIDTH - 500))
                    if x.newPos[1] < 500:
                        cordOffset[1] -= (500 - x.newPos[1])
                    if x.newPos[1] > (WINDOWHEIGHT - 500):
                        cordOffset[1] += (x.newPos[1] - (WINDOWHEIGHT - 500))

            for x in projectiles:
                x.draw(cordOffset)

            # Check for outranged projectiles
            for x in projectiles:
                if x.range <= 0:
                    try:
                        del projectiles[projectiles.index(x)]
                    except:
                        logging.warning("Projectile not deletet")

            # Display the hud
            for x in towers:
                x.healthBar()

            for x in characters:
                x.healthBar()

            for x in dots:
                x.draw(cordOffset)

            # Health text and bar
            healthText.draw(f"{round(characters[char].health, 1)}/{round(characters[char].maxHealth, 1)}")

            # Level, resources & curent item
            levelText.draw(f"Level: {characters[char].level}")

            resourcesText.draw(f"Resources: {round(characters[char].resources, 1)}")
                    
            equippedItemIconText.draw(f"{items[0].displayName}: {characters[char].inventory.get(items[0].name).amount}")

            for x in characters[char].effect:
                effectIconText.icon = images.get(x.type)
                # Refine string out effect type
                text = str(x.type)[:1].upper() + str(x.type)[1:]
                effectIconText.draw(text)

            # Debug infos
            if hudMode == 1:
                fpsText.draw(f"FPS: {int(clock.get_fps())}")

        elif screen == "game_paused" or screen == "death_screen":
            py.draw.rect(gamesurf, GREY, (resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1]))
            resetButton = py.Rect(resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1])

            py.draw.rect(gamesurf, GREY, (menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1]))
            menuButton = py.Rect(menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1])

            # Print current title
            if screen == "game_paused":
                pauseText.draw("Paused")
            else:
                deadText.draw("You are Dead")

            resetText.draw("Restart")

            menuText.draw("Main Menu")

        elif screen == "game_inventory":
            pass

        # Updating the display
        py.display.update()

        # Tick the main clock with given fps
        if setFPS <= 0 or setFPS >= 120:
            clock.tick(120)
        else:
            clock.tick(setFPS)

# Catch any error an add it to the crash log
except:
    logging.critical(traceback.format_exc())

# Doing final cleanup
finally:
    # Stops all pygame modules and closes all windows
    py.quit()
    # Prints end of log
    logging.info(f"Stopping after: {round(ti.time()-startTime, 3)} s")