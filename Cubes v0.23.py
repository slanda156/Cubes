import pygame as py
import math
import random as ra

# Import classes

from damageTypes import damageTypes
from weapons import *
from armor import *
from item import *
from upgrade import *

# Define the window
i = 0
setFPS = 60
QUALITY = (16, 9)
WINDOWWIDTH = 2040
WINDOWHEIGHT = int((WINDOWWIDTH/QUALITY[0])*QUALITY[1])

# Contorls

# WASD      :   Movement
# T         :   Skip Build Time
# F         :   Place Tower     |BUG|
# E         :   Use Equiped Item (Currently just Medkits)
# TAB       :   Switch Hud Modes (0: Nothin; 1: Health; 2: 1 & Level, Resources; 3: 2 & XP, Reload, Status; 4: 3 & Performance)
# Spacebar  :   Mind Transfer   |BUG|
# LMB       :   Shoot
# RMB       :   Teleport        |BUG|

version = "0.23"

# Define Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTGREY = (169, 169, 169)
GREY = (100, 100, 100)
RED = (255, 0, 0)
LIGHTRED = (230, 95, 57)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ERROCOLOR = (255, 0, 102)

# Define Fonts

py.font.init()

buttonFont = py.font.SysFont("Comic Sans Ms", 24)
titleFont = py.font.SysFont("Comic Sans Ms", 35)

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

if_break = False
playing = False
pause = False
dead = False

movement = "none"

levelText = None

characters = []
towers = []
projectiles = []
barriers = []
spawnPoints = []

downTriangle = [py.Vector2(0, 0), py.Vector2(20, 0), py.Vector2(10, 10)]
upTriangle = [py.Vector2(0, 10), py.Vector2(20, 10), py.Vector2(10, 0)]

viewMode = 2
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

class barrier:
    def __init__(self, pos, size, death=False):
        self.pos = pos
        self.size = size
        self.death = death

    def draw(self):
        if self.death:
            py.draw.rect(gamesurf, RED, (self.pos[0], self.pos[1], self.size[0], self.size[1]))
        else:
            py.draw.rect(gamesurf, LIGHTGREY, (self.pos[0], self.pos[1], self.size[0], self.size[1]))

class spawnPoint:
    def __init__(self, pos, team):
        self.pos = pos
        self.team = team
        self.maxCooldown = 5
        self.minCooldown = 2
        self.cooldown = self.maxCooldown

    def draw(self):
        py.draw.rect(gamesurf, GREY, (self.pos[0]-30, self.pos[1]-30, 60, 60))
        py.draw.rect(gamesurf, GREEN, (self.pos[0]-25, self.pos[1]-25, 50, 50))

    def spawn(self):
        if self.team != 0 and len(characters) < maxChar + 1:
            if self.cooldown <= 0:
                allowedWeapons = []
                allowedWeaponTypes = []
                if characters[findPlayerChar()].level // 1 >= 1:
                    allowedWeaponTypes.append(physical)

                elif characters[findPlayerChar()].level // 3 >= 3:
                    allowedWeaponTypes.append(fire)

                elif characters[findPlayerChar()].level // 6 >= 6:
                    allowedWeaponTypes.append(plasma)

                elif characters[findPlayerChar()].level // 9 >= 9:
                    allowedWeaponTypes.append(laser)

                for y in allowedWeaponTypes:
                    for x in weapons:
                        if x.type == y:
                            allowedWeapons.append(x)

                if len(allowedWeapons) > 1:
                    weaponIn = ra.randrange(0, (len(allowedWeapons)-1))
                else:
                    weaponIn = 0
                armorIn = ra.randrange(0, armorNum)

                characters.append(character(self.pos, self.team, allowedWeapons[weaponIn], armors[armorIn], baseSpeed))

                self.cooldown = ra.randint(self.minCooldown, self.maxCooldown)
            else:
                self.cooldown -= time

class projectile:
    def __init__(self, start, dierection, power, weapon, team):
        self.start = start
        self.dierection = dierection
        self.power = int(power)
        self.pos = 0
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

    def draw(self):
        #self.offset.scale_to_length(self.weapon.speed/1000 * time) # FIX

        if self.weapon.type == plasma:
            py.draw.circle(gamesurf, self.weapon.color, (int(self.start[0]), int(self.start[1])), int(self.power/2))
        else:
            if self.power < 5:
                py.draw.line(gamesurf, self.weapon.color, self.start, (self.start + self.dierection), self.power*2)
            else:
                py.draw.line(gamesurf, self.weapon.color, self.start, (self.start + self.dierection), self.power*2)

        self.start += self.offset
        self.range -= self.offset.length()

class effect:
    def __init__(self, effectType, effectDuration, effectDamage):
        self.type = effectType
        self.duration = effectDuration
        self.damage = effectDamage

class tower:
    def __init__(self, pos, team, weapon, level, accuracy):
        self.team = team
        self.type = "tower"
        self.weapon = weapon
        self.level = level
        self.seq = 0
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

    def draw(self):
        for x in self.effect:
            if x.type == self.armor.type:
                self.health -= x.damage
            else:
                self.health -= x.damage

            if x.duration <= 0:
                pass

        self.target = py.mouse.get_pos()

        if getNearestEnemieChar(self) != None:
            self.target = getNearestEnemieChar(self).pos

        if not checkList(self.effect, "shocked"):
            self.dir = py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1])
            self.dir.scale_to_length(int(self.radius*(self.factor+0.2)))

        if self.cooldown <= 0:
            self.shoot(self.target)

        if self.cooldown > 0:
            self.cooldown -= time

        py.draw.rect(gamesurf, GREY, ((self.pos[0]-(self.size[0]/2)), (self.pos[1]-(self.size[1]/2)), self.size[0], self.size[1]))

        py.draw.circle(gamesurf, RED, self.pos, self.radius)

        py.draw.line(gamesurf, self.weapon.color, self.pos, (self.pos + self.dir), int(self.radius/4))

    def getHit(self, weapon):
        self.effectDuration = weapon.effectDuration

        if weapon.effect != None:
            self.effect.append(effect(weapon.type, weapon.effectDuration, weapon.effectDamage))

        if self.armor.type == weapon.type:
            self.health -= weapon.damage/2

        else:
            self.health -= weapon.damage

    def shoot(self, target):
        appendProjectiles(self.pos, py.Vector2(target[0]-self.pos[0], target[1]-self.pos[1]), self.weapon.power, self.weapon, self.team, self.accuracy)

        self.cooldown = self.maxCooldown

    def healthBar(self):
        pos = self.pos + py.Vector2(0, -20)

        py.draw.rect(gamesurf, GREY, (pos[0]-20, pos[1]-6, 40, 12))

        py.draw.rect(gamesurf, LIGHTGREY, (pos[0]-18, pos[1]-4, 36, 8))

        i = self.health / self.maxHealth

        py.draw.rect(gamesurf, RED, (pos[0]-18, pos[1]-4, int(36*i), 8))

class character:
    def __init__(self, pos, team, weapon, armor, speed):
        self.pos = [pos[0], pos[1]]
        self.seq = 0
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

    def draw(self):
        if self.armor.type == physical:
            self.maxHealth = float(10 * self.level * 2)
        else:
            self.maxHealth = float(10 * self.level)

        if self.boost > self.maxBoost:
            self.boost = self.maxBoost

        if self.charge < self.maxCharge:
            self.charge += time*10

        if self.xp >= (self.level * 100):
            self.xp = 0
            self.level += 1

        for x in self.effect:
            if x.type == self.armor.type:
                self.health -= (x.damage*time)/2
            else:
                self.health -= x.damage*time

            if x.duration <= 0:
                pass

        if self.team == 0:
            self.target = py.mouse.get_pos()
        else:
            self.target = characters[findPlayerChar()].pos

        if not checkList(self.effect, "shocked"):
            self.dir = py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1])
            if self.team != 0:
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
                    self.pos[0] -= int(self.dir[0])
                    self.pos[1] -= int(self.dir[1])

        py.draw.circle(gamesurf, (200, 200, 200), (int(self.pos[0]), int(self.pos[1])), self.radius)

        if self.dir.length() != 0:
            self.dir.scale_to_length(30)

        py.draw.line(gamesurf, self.weapon.color, self.pos, (self.pos + self.dir), int(self.radius/4))

        py.draw.circle(gamesurf, self.armor.color, (int(self.pos[0]), int(self.pos[1])), int(self.radius/3))

        self.cooldown -= time

        if self.team != 0 and self.cooldown <= 0 and not checkList(self.effect, "shocked"):
            if calcDist(self.pos, self.target) < self.weapon.range:
                self.shoot()

        for x in self.effect:
            if x.duration > 0:
                x.duration -= time

    def getHit(self, weapon):
        self.effectDuration = weapon.effectDuration

        if weapon.effect != None:
            self.effect.append(effect(weapon.type, weapon.effectDuration, weapon.damage/10))

        if self.armor.type == weapon.type:
            self.health -= weapon.damage/2

        else:
            self.health -= weapon.damage

    def healthBar(self):
        pos = self.pos + py.Vector2(0, -20)

        py.draw.rect(gamesurf, GREY, (pos[0]-20, pos[1]-6, 40, 12))

        py.draw.rect(gamesurf, LIGHTGREY, (pos[0]-18, pos[1]-4, 36, 8))

        i = self.health / self.maxHealth

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

# Declare Functions

def findPlayerChar():
    for x in characters:
        if x.team == 0:
            return x.seq

def canSeeTarget(start, target):
    if True and True:
        return True
    else:
        return False

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
                if y.type == "tower" and checkRectangle():
                    y.getHit(x.weapon)
                elif y.type == "player" and checkCircle(y, x, y.radius):
                    y.getHit(x.weapon)
                    if y.health <= 0:
                        if x.team == 0:
                            i = findPlayerChar()
                            characters[i].xp += (characters[i].level*20)        #FIX
                            characters[i].resources += ((y.level/3)*20)

                    try:
                        del projectiles[x.pos]
                    except IndexError:
                        print(f"Projectile not deletet, pos: {x.pos}")

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

    return(distance.length())

def positiveNum(number):
    if number < 0:
        number -= number*2

    return number

def sculpt(pos, texture, offset):
    return True

def getNearestChar(start):
    distance = []
    minDist = [0, 0]
    if len(characters) > 1:
        for x in characters:
            distance.append((calcDist(start.pos, x.pos), characters[char].seq))

        for y in distance:
            if minDist[0] > y[0]:
                minDist = y

        return characters[minDist[1]]

def getNearestFriendlyChar(start):
    distance = []
    minDist = [0, 0]
    if len(characters) > 1:
        for x in characters:
            if start.team == x.team:
                distance.append((calcDist(start.pos, x.pos), characters[char].seq))

        for y in distance:
            if minDist[0] > y[0]:
                minDist = y

        return characters[minDist[1]]

def getNearestEnemieChar(start):
    distance = []
    minDist = [0, 0]

    if len(characters) > 1:
        for x in characters:
            if start.team != x.team:
                distance.append((calcDist(start.pos, x.pos), characters[char].seq))

        for y in distance:
            if minDist[0] > y[0]:
                minDist = y

        return characters[minDist[1]]

def mindTransport(start, target):
    characters[target.seq].team = 0
    characters[start.seq].team = 1

def die():
    playing = False # Temporary
    dead = True
    reset()

def reset():
    gamesurf.fill(BLACK)
    py.event.clear()

    global levelText
    global barriers
    global characters
    global spawnPoints
    global projectiles
    global baseSpeed
    global towers

    oldWeapon = weapons[0]
    oldArmor = armors[0]

    if len(characters) > 0:
        oldWeapon = characters[findPlayerChar()].weapon
        oldArmor = characters[findPlayerChar()].armor

    characters = []
    projectiles = []
    barriers = []
    spawnPoints = []
    towers = []

    pos = (ra.randrange(100, WINDOWWIDTH-100), ra.randrange(100, WINDOWHEIGHT-100))
    characters.append(character(pos, 0, oldWeapon, oldArmor, baseSpeed))

    while len(spawnPoints) < 5:
        fails = 0
        if fails > 20:
            break

        pos = (ra.randrange(50, WINDOWWIDTH-50), ra.randrange(50, WINDOWHEIGHT-50))
        if len(spawnPoints) <= 0:
            spawnPoints.append(spawnPoint(pos, 1))

        else:
            for x in spawnPoints:
                if calcDist(x.pos, pos) > 500:
                    spawnPoints.append(spawnPoint(pos, 1))
                else:
                    fails += 1

    #for x in spawnPoints:  # To laggie
    #    toSpawn = 8
    #    while toSpawn > 0:
    #        position = (ra.randrange(x.pos[0]-500, x.pos[0]+500), ra.randrange(x.pos[1]-500, x.pos[1]+500))
    #        if position[0] > 50 and position[1] > 50 and position[0] < WINDOWWIDTH-50 and position[1] < WINDOWHEIGHT-50:
    #            distance = calcDist(x.pos, position)
    #            if distance > 50 and distance < 500:
    #                for y in barriers:
    #                    if calcDist(position, y.pos) > 40:
    #                        toSpawn -= 1
    #                        size = (ra.randrange(20, 50), ra.randrange(20, 50))
    #                        barriers.append(barrier(position, size))

    barriers.append(barrier((0, 0), (WINDOWWIDTH, 10)))

    barriers.append(barrier((0, 0), (10, WINDOWHEIGHT)))

    barriers.append(barrier((0, WINDOWHEIGHT-10), (WINDOWWIDTH, 10)))

    barriers.append(barrier((WINDOWWIDTH-10, 0), (10, WINDOWHEIGHT)))

# Initialsation

if py.get_init() == False:
    py.init()

gamesurf = py.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

py.display.set_caption(f"Cubes v.{version}")

clock = py.time.Clock()

initArmor()
initWeapon()
initItem()
initUpgrade()

armorText = textWidget(buttonFont, armors[0].color, ((WINDOWWIDTH/2)-70, (WINDOWHEIGHT/4)+15), gamesurf)
weaponText = textWidget(buttonFont, weapons[0].color, ((WINDOWWIDTH/2)-70, (WINDOWHEIGHT/4)+90), gamesurf)

# Main Loop

reset()

while True:
    if if_break:
        break

    gamesurf.fill(BLACK)
    time = (clock.get_time() / 1000)
    char = findPlayerChar()

    if characters[char].level <= 10:
        maxChar = characters[char].level
    else:
        maxChar = 10

    if playing:
        if dead:
            resetButtonSize = (150, 40)
            resetButtonPos = ((WINDOWWIDTH//2)-(resetButtonSize[0]//2), (WINDOWHEIGHT//2)-(resetButtonSize[1]//2))

            menuButtonSize = (150, 40)
            menuButtonPos = ((WINDOWWIDTH//2)-(menuButtonSize[0]//2), (WINDOWHEIGHT//2)-menuButtonSize[1]//2+50)

            py.draw.rect(gamesurf, GREY, (resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1]))
            resetButton = py.Rect(resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1])

            py.draw.rect(gamesurf, GREY, (menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1]))
            menuButton = py.Rect(menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1])

            resetText = textWidget(buttonFont, BLACK, (resetButtonPos[0]+(resetButtonSize[0]*0.22), resetButtonPos[1]), gamesurf)
            resetText.draw("Play Again")

            menuText = textWidget(buttonFont, BLACK, (menuButtonPos[0]+(menuButtonSize[0]*0.1), menuButtonPos[1]), gamesurf)
            menuText.draw("Main Menu")

            for event in py.event.get():
                if event.type == py.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if resetButton.collidepoint(py.mouse.get_pos()):
                            reset()
                            pause = False

                        elif menuButton.collidepoint(py.mouse.get_pos()):
                            playing = False
                            pause = False
                            break

        else:
            if pause:
                resetButtonSize = (150, 40)
                resetButtonPos = ((WINDOWWIDTH//2)-(resetButtonSize[0]//2), (WINDOWHEIGHT//2)-(resetButtonSize[1]//2))

                menuButtonSize = (150, 40)
                menuButtonPos = ((WINDOWWIDTH//2)-(menuButtonSize[0]//2), (WINDOWHEIGHT//2)-menuButtonSize[1]//2+50)

                py.draw.rect(gamesurf, GREY, (resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1]))
                resetButton = py.Rect(resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1])

                py.draw.rect(gamesurf, GREY, (menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1]))
                menuButton = py.Rect(menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1])

                resetText = textWidget(buttonFont, BLACK, (resetButtonPos[0]+(resetButtonSize[0]*0.22), resetButtonPos[1]), gamesurf)
                resetText.draw("Restart")

                menuText = textWidget(buttonFont, BLACK, (menuButtonPos[0]+(menuButtonSize[0]*0.1), menuButtonPos[1]), gamesurf)
                menuText.draw("Main Menu")

            for event in py.event.get():
                if event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE:
                        if pause:
                            pause = False
                        else:
                            pause = True

                    elif event.key == py.K_SPACE and not pause:
                        pass
                        #mindTransport(characters[char], getNearestChar(characters[char]))

                    elif event.key == py.K_t and waveCooldown != 0:
                        waveCooldown = 0
                        oldLevel = characters[char].level

                    elif event.key == py.K_f and characters[char].resources >= characters[char].towerCost and not pause:
                        appendTower(characters[char].pos, characters[char].team, characters[char].towerWeapon, characters[char].level, characters[char].towerAccuracy)

                    elif event.key == py.K_e and characters[char].resources >= items[findObjectInList(items, "medKit")].cost and not pause:
                        characters[char].health += items[findObjectInList(items, "medKit")].healing

                        if characters[char].health > characters[char].maxHealth:
                            characters[char].health = characters[char].maxHealth

                    elif event.key == py.K_TAB:
                        viewMode += 1

                        if viewMode < 0:
                            viewMode = 4

                        elif viewMode > 4:
                            viewMode = 0

                elif event.type == py.MOUSEBUTTONDOWN:
                    if pause:
                        if event.button == 1:
                            if resetButton.collidepoint(py.mouse.get_pos()):
                                reset()
                                pause = False

                            elif menuButton.collidepoint(py.mouse.get_pos()):
                                playing = False
                                pause = False
                                break

                    else:
                        if event.button == 2 and characters[char].charge >= 100:
                            characters[char].pos = py.mouse.get_pos()
                            characters[char].effect.append("shocked")
                            characters[char].effectDuration = 2.5

            if not pause:
                mouse = py.mouse.get_pressed()

                if mouse[0] == 1 and not checkList(characters[char].effect, "shocked") and characters[char].cooldown <= 0:
                    characters[char].shoot()

                keys = py.key.get_pressed()

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

                if oldLevel != characters[char].level:
                    if (characters[char].level % 10) == 0 and waveCooldown <= 0:
                        waveCooldown = 30
                        oldLevel = characters[char].level

                if waveCooldown > 0:
                    for x in characters:
                        if x.team != 0:
                            del characters[x.seq]
                    waveCooldownText = textWidget(titleFont, GREEN, (WINDOWWIDTH/2, 20), gamesurf)
                    waveCooldownText.draw(round(waveCooldown, 1))
                    waveCooldown -= time

                #for x in characters:
                #    for y in barriers:
                #        checkCollision(x, y)

                checkHits(projectiles, characters)

                for x in projectiles:
                    for y in barriers:
                        if checkRectangle(y, x):
                            try:
                                del projectiles[x.pos]
                            except:
                                print(f"Projectile not deletet, pos: {x.pos}")

                for x in range(0, len(projectiles)):
                    projectiles[x].pos = x

                for x in range(0, len(towers)):
                    towers[x].seq = x

                for x in range(0, len(characters)):
                    characters[x].seq = x

                for x in characters:
                    if x.health <= 0:
                        if x.team == 0:
                            die()
                            break

                        else:
                            try:
                                del characters[x.seq]
                            except:
                                print(f"Cant delete character: {x.seq}")

                for x in spawnPoints:
                    x.draw()
                    if waveCooldown <= 0:
                        x.spawn()

                for x in barriers:
                    x.draw()

                for x in towers:
                    x.draw()

                for x in characters:
                    x.draw()

                for x in projectiles:
                    if x.range <= 0:
                        try:
                            del projectiles[x.pos]
                        except:
                            print(f"Cant Delete Projectile {x.pos}")

                for x in projectiles:
                    x.draw()

                if viewMode > 0:
                    for x in towers:
                        x.healthBar()

                    for x in characters:
                        x.healthBar()

                if viewMode > 0:
                    healthText = textWidget(buttonFont, LIGHTRED, (20, 20), gamesurf)
                    healthText.draw(f"{round(characters[char].health, 1)}/{round(characters[char].maxHealth, 1)}")

                if viewMode > 1:
                    levelText = textWidget(buttonFont, GREEN, (20, 50), gamesurf)
                    levelText.draw(f"Level: {characters[char].level}")

                    resourcesText = textWidget(buttonFont, GREEN, ((WINDOWWIDTH-200), 20), gamesurf)
                    resourcesText.draw(f"Resources: {round(characters[char].resources, 1)}")

                if viewMode > 2:
                    xpText = textWidget(buttonFont, GREEN, (20, 80), gamesurf)
                    xpText.draw(f"XP: {int(characters[char].xp)}/{characters[char].level*100}")

                if viewMode > 3:
                    fpsText = textWidget(buttonFont, GREEN, ((WINDOWWIDTH-180), 60), gamesurf)
                    fpsText.draw(f"FPS: {int(clock.get_fps())}")

    else:
        py.draw.rect(gamesurf, GREY, ((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+50, 180, 40))
        playRect = py.Rect((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+50, 180, 40)

        playText = textWidget(buttonFont, BLACK, ((WINDOWWIDTH/2)-30, (WINDOWHEIGHT/3)+50), gamesurf)
        playText.draw("PLAY")

        upPos1 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4)+130)
        downPos1 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4)+80)
        upPos2 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4)+50)
        downPos2 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4))

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

        quitText = textWidget(buttonFont, BLACK, ((WINDOWWIDTH/2)-35, (WINDOWHEIGHT/3)+100), gamesurf)
        quitText.draw("QUIT")

        for event in py.event.get():
            if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                if playRect.collidepoint(py.mouse.get_pos()):
                    playing = True
                    reset()

                elif upWeaponButtonRect.collidepoint(py.mouse.get_pos()):
                    weaponIndex += 1

                elif downWeaponButtonRect.collidepoint(py.mouse.get_pos()):
                    weaponIndex -= 1

                elif upArmorButtonRect.collidepoint(py.mouse.get_pos()):
                    armorIndex += 1

                elif downArmorButtonRect.collidepoint(py.mouse.get_pos()):
                    armorIndex -= 1

                elif quitButton.collidepoint(py.mouse.get_pos()):
                    py.display.quit()
                    if_break = True

        if weaponIndex < 0:
            weaponIndex = weaponNum-1

        elif weaponIndex > (weaponNum-1):
            weaponIndex = 0

        if armorIndex < 0:
            armorIndex = armorNum-1

        elif armorIndex > (armorNum-1):
            armorIndex = 0

        weaponText.color = weapons[weaponIndex].color
        armorText.color = armors[armorIndex].color

        weaponText.draw(weapons[weaponIndex].displayName)
        armorText.draw(armors[armorIndex].displayName)

        characters[char].weapon = weapons[weaponIndex]
        characters[char].armor = armors[armorIndex]

    if if_break == False:
        py.display.update()

    if setFPS <= 0 or setFPS >= 120:
        clock.tick(120)
    else:
        clock.tick(setFPS)
