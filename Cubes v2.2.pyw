import pygame as py
import math
import random as ra

# Define the window
i = 0
QUALITY = (16, 9)
WINDOWWIDTH = 2040
WINDOWHEIGHT = int((WINDOWWIDTH/QUALITY[0])*QUALITY[1])

# Define Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
LIGHTGREY = (169,169,169)
GREY = (100,100,100)
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)

# Define Textures
boss = {
    0,0,0,0,0,0,0,0,
    0,0,1,0,0,1,0,0,
    0,1,0,1,1,0,1,0,
    1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,
    0,0,1,1,1,1,0,0,
    0,0,1,0,0,1,0,0,
    0,0,0,0,0,0,0,0
}

# Define Variables

if_break = False
playing = False

movement = "none"

characters = []
projectiles = []
barriers = []
spawnPoints = []

maxChar = 0
time = 0
baseSpeed = 150 # pixel/s

# Weapon Types

electric = "electric"
fire = "fire"
physical = "physical"

# Initialsation

if py.get_init() == False:
    py.init()
gamesurf = py.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
py.display.set_caption('Cubes (FAST)')
clock = py.time.Clock()

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
        global time
        self.pos = pos
        self.team = team
        self.cooldown = 2.5 # in milliseconds
    def draw(self):
        py.draw.rect(gamesurf, GREY, (self.pos[0]-30, self.pos[1]-30, 60, 60))
        py.draw.rect(gamesurf, GREEN, (self.pos[0]-25, self.pos[1]-25, 50, 50))
    def spawn(self):
        global maxChar
        global baseSpeed
        if self.team != 0 and len(characters) < maxChar + 1:
            if self.cooldown <= 0:
                weaponNum = ra.randint(0, 2)
                weaponType = physical
                if weaponNum == 1:
                    weaponType = fire
                elif weaponNum == 2:
                    weaponType = electric
                resistanceNum = ra.randint(0, 2)
                resistance = physical
                if resistanceNum == 1:
                    resistance = fire
                elif resistanceNum == 2:
                    resistance = electric
                characters.append(character(self.pos, self.team, weaponType, resistance, ra.randrange(1, 10), baseSpeed))
                self.cooldown = 2.5
            else:
                self.cooldown -= time

class projectile:
    def __init__(self, start, startChar, dierection, baseRange, power, type, baseDamage, team):
        global time
        self.start = start
        self.startChar = startChar
        self.dierection = dierection
        self.range = (baseRange * 2) * power
        self.power = power
        self.type = type
        self.pos = 0
        self.team = team
        if self.type == fire:
            self.damage = (baseDamage * (power / 10)) / 10
            self.dierection.scale_to_length(int(self.power))
            self.speed = 220
        elif self.type == electric:
            self.damage = (baseDamage * (power / 10)) / 2
            self.dierection.scale_to_length(int(self.power * 3))
            self.speed = 340
        else:
            self.damage = baseDamage * (power / 10)
            self.dierection.scale_to_length(int(self.power * 2))
            self.speed = 400
        self.offset = self.dierection
    def draw(self):
        self.offset.scale_to_length(self.speed * time)
        if self.type == fire:
            color = RED
        elif self.type == electric:
            color = BLUE
        else:
            color = GREY
        if self.power < 5:
            py.draw.line(gamesurf, color, self.start, (self.start + self.dierection), self.power*2)
        else:
            py.draw.line(gamesurf, color, self.start, (self.start + self.dierection), self.power)
        self.start += self.offset
        self.range -= self.offset.length()

class character:
    def __init__(self, pos, team, weaponType, resistance, armor, speed):
        self.pos = [pos[0], pos[1]]        
        self.seq = 0
        self.team = team
        self.weaponType = weaponType
        self.resistance = resistance
        self.armor = armor
        self.cooldown = 0
        self.target = [0, 0]
        self.level = 1
        self.xp = 0
        if self.resistance == physical:
            self.maxHealth = 10 * self.level * 2
        else:
            self.maxHealth = 10 * self.level
        self.health = self.maxHealth
        self.boost = 100
        self.effect = []
        self.effectDuration = 0
        self.effectDamage = 0
        self.radius = 20
        if self.resistance == physical:
            self.movementSpeed = int(speed * 0.8)
        else:
            self.movementSpeed = int(speed)
    def draw(self):
        global time
        if self.xp >= (self.level * 100):
            self.xp = 0
            self.level += 1
        if checkList(self.effect, "fire") and self.effectDuration > 0:
            if self.resistance == fire:
                self.health -= self.effectDamage / 2
            else:
                self.health -= self.effectDamage
        elif checkList(self.effect, "shocked") and self.effectDuration > 0:
            if self.resistance == electric:
                self.health -= self.effectDamage / 2
            else:
                self.health -= self.effectDamage
        elif self.effectDuration <= 0:
            del self.effect
            self.effect = []
        if self.team == 0:
            self.target = py.mouse.get_pos()
        else:
            self.target = characters[findPlayerChar()].pos
        if not checkList(self.effect, "shocked"):
            self.dir = py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1])
            if self.team != 0:
                if self.dir.length() != 0:
                    self.dir.scale_to_length(int(self.movementSpeed * time))
                if calcDist(self.pos, self.target) > 200:
                    self.pos[0] += int(self.dir[0])
                    self.pos[1] += int(self.dir[1])
                else:
                    self.pos[0] -= int(self.dir[0])
                    self.pos[1] -= int(self.dir[1])
        py.draw.circle(gamesurf, (200, 200, 200), (int(self.pos[0]), int(self.pos[1])), self.radius)
        if self.weaponType == fire:
            color = RED
        elif self.weaponType == electric:
            color = BLUE
        else:
            color = GREY
        if self.dir.length() != 0:
            self.dir.scale_to_length(30)
        py.draw.line(gamesurf, color, self.pos, (self.pos + self.dir), int(self.radius/4))
        if self.resistance == fire:
            color = RED
        elif self.resistance == electric:
            color = BLUE
        else:
            color = GREY
        py.draw.circle(gamesurf, color, (int(self.pos[0]), int(self.pos[1])), int(self.radius/4))
        self.cooldown -= time
        if self.team != 0 and self.cooldown <= 0 and not checkList(self.effect, "shocked"):
            self.shoot()
        if self.effectDuration > 0:
            if self.resistance == electric:
                self.effectDuration -= 2
            else:
                self.effectDuration -= 1
    def getHit(self, damage, type):
        if type == fire:
            self.effectDuration = 50
            if not checkList(self.effect, "fire"):
                self.effect.append("fire")
            self.effectDamage = damage / 2
        elif type == electric:
            self.effectDuration = 20
            if not checkList(self.effect, "shocked"):
                self.effect.append("shocked")
        if self.resistance == type:
            self.health -= damage/2
        else:
            self.health -= damage
    def healthBar(self):
        pos = self.pos + py.Vector2(0, -20)
        py.draw.rect(gamesurf, GREY, (pos[0]-20, pos[1]-6, 40, 12))
        py.draw.rect(gamesurf, LIGHTGREY, (pos[0]-18, pos[1]-4, 36, 8))
        i = self.health / self.maxHealth
        py.draw.rect(gamesurf, RED, (pos[0]-18, pos[1]-4, int(36*i), 8))
    def shoot(self):
        if self.cooldown <= 0 and not checkList(self.effect, "shocked"):
            print("shoot")
            if self.weaponType == fire:
                appendProjectiles(self.pos, self.seq, py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1]), 20, 5, self.weaponType, self.level * 2, self.team)
                self.cooldown = ra.randrange(200, 400)/1000
            elif self.weaponType == electric:
                appendProjectiles(self.pos, self.seq, py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1]), 40, 5, self.weaponType, self.level * 2, self.team)
                self.cooldown = ra.randrange(800, 1200)/1000
            else:
                appendProjectiles(self.pos, self.seq, py.Vector2(self.target[0]-self.pos[0], self.target[1]-self.pos[1]), 80, 5, self.weaponType, self.level * 2, self.team)
                self.cooldown = 1500/1000

# Declare Functions

def findPlayerChar():
    global characters
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
        print(hyp, vector.length(), sep=', ')
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
        if x == var:
            return True
        else:
            return False

def checkHits(projectiles, objects):
    for x in projectiles:
        for y in objects:
            if checkCircle(y, x, y.radius):
                if x.team != y.team:
                    if characters[x.startChar].team == 0:
                        characters[x.startChar].xp += ((y.level/2)*10)
                    y.getHit(x.damage, x.type)
                    del projectiles[x.pos]

def offsetTrajectory(start, splatter):
    start[0] = int(start[0])
    start[1] = int(start[1])
    return py.Vector2(ra.randint(start[0]-splatter, start[0]+splatter), ra.randint(start[1]-splatter, start[1]+splatter))

def appendProjectiles(start, startChar, dierection, baseRange, power, type, baseDamage, team):
    if type == fire:
        i = ra.randint(3, 5)
        #while i > 0:
        dierection += offsetTrajectory(dierection, 100)
        projectiles.append(projectile(start, startChar, dierection, baseRange, power, type, baseDamage, team))
        i -= 1
    elif type == electric:
        dierection += offsetTrajectory(dierection, 10)
        projectiles.append(projectile(start, startChar, dierection, baseRange, power, type, baseDamage, team))
    else:
        projectiles.append(projectile(start, startChar, dierection, baseRange, power, type, baseDamage, team))

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
    global characters
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
    global characters
    characters[target.seq].team = 0
    characters[start.seq].team = 1

def reset():
    gamesurf.fill(BLACK)
    py.event.clear()
    global barriers
    global characters
    global spawnPoints
    global projectiles
    global baseSpeed
    del barriers
    del characters
    del spawnPoints
    del projectiles
    characters = []
    projectiles = []
    barriers = []
    spawnPoints = []
    pos = (ra.randrange(100, WINDOWWIDTH-100), ra.randrange(100, WINDOWHEIGHT-100))
    characters.append(character(pos, 0, physical, physical, 2, baseSpeed))
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
                    print()
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

    #barriers.append(barrier((WINDOWWIDTH/2, WINDOWHEIGHT/2), (50, 50)))
    barriers.append(barrier((100, 100), (50, 50)))

# Main Loop

reset()

while True:
    if if_break:
        break
    gamesurf.fill(BLACK)
    time = (clock.get_time() / 1000)
    char = findPlayerChar()
    if characters[char].level <= 5:
        maxChar = characters[char].level
    else:
        maxChar = 10
    if playing:
        for event in py.event.get():
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    if playing:
                        playing = False
                        reset()
                    else:
                        py.display.quit()
                        if_break = True
                elif event.key == py.K_SPACE:
                    pass
                    #mindTransport(characters[char], getNearestChar(characters[char]))
        mouse = py.mouse.get_pressed()
        if mouse[0] == 1:
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

        #for x in characters:
        #    for y in barriers:
        #        checkCollision(x, y)
        checkHits(projectiles, characters)
        for x in projectiles:
            for y in barriers:
                if checkRectangle(y, x):
                    del projectiles[x.pos]

        if playing:
            for x in range(0, len(projectiles)):
                projectiles[x].pos = x
            for x in range(0, len(characters)):
                characters[x].seq = x
            for x in characters:
                if x.health <= 0:
                    if x.team == 0:
                        reset()
                        break
                    else:
                        del characters[x.seq]
            for x in spawnPoints:
                x.draw()
                x.spawn()
            for x in barriers:
                x.draw()
            for x in characters:
                x.draw()
                x.healthBar()
            for x in projectiles:
                if x.range <= 0:
                    del projectiles[x.pos]
            for x in projectiles:
                x.draw()
            print("XP: ", characters[char].xp, ", Level: ", characters[char].level)
    else:
        py.draw.rect(gamesurf, GREY, ((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)-20, 180, 40))
        playRect = py.Rect((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)-20, 180, 40)

        py.draw.rect(gamesurf, GREY, ((WINDOWWIDTH/2)-55, (WINDOWHEIGHT/3)-20-30, 30, 20))
        weapon1Rect = py.Rect((WINDOWWIDTH/2)-55, (WINDOWHEIGHT/3)-20-30, 30, 20)

        py.draw.rect(gamesurf, RED, ((WINDOWWIDTH/2)-15, (WINDOWHEIGHT/3)-20-30, 30, 20))
        weapon2Rect = py.Rect((WINDOWWIDTH/2)-15, (WINDOWHEIGHT/3)-20-30, 30, 20)

        py.draw.rect(gamesurf, BLUE, ((WINDOWWIDTH/2)+25, (WINDOWHEIGHT/3)-20-30, 30, 20))
        weapon3Rect = py.Rect((WINDOWWIDTH/2)+25, (WINDOWHEIGHT/3)-20-30, 30, 20)

        py.draw.rect(gamesurf, GREY, ((WINDOWWIDTH/2)-55, (WINDOWHEIGHT/3)-20-60, 30, 20))
        armor1Rect = py.Rect((WINDOWWIDTH/2)-55, (WINDOWHEIGHT/3)-20-60, 30, 20)

        py.draw.rect(gamesurf, RED, ((WINDOWWIDTH/2)-15, (WINDOWHEIGHT/3)-20-60, 30, 20))
        armor2Rect = py.Rect((WINDOWWIDTH/2)-15, (WINDOWHEIGHT/3)-20-60, 30, 20)

        py.draw.rect(gamesurf, BLUE, ((WINDOWWIDTH/2)+25, (WINDOWHEIGHT/3)-20-60, 30, 20))
        armor3Rect = py.Rect((WINDOWWIDTH/2)+25, (WINDOWHEIGHT/3)-20-60, 30, 20)

        for event in py.event.get():
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    if playing:
                        playing = False
                        reset()
                    else:
                        py.display.quit()
                        if_break = True
            elif event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                if playRect.collidepoint(py.mouse.get_pos()):
                    playing = True
                elif weapon1Rect.collidepoint(py.mouse.get_pos()):
                    characters[char].weaponType = physical
                elif weapon2Rect.collidepoint(py.mouse.get_pos()):
                    characters[char].weaponType = fire
                elif weapon3Rect.collidepoint(py.mouse.get_pos()):
                    characters[char].weaponType = electric
                elif armor1Rect.collidepoint(py.mouse.get_pos()):
                    characters[char].resistance = physical
                elif armor2Rect.collidepoint(py.mouse.get_pos()):
                    characters[char].resistance = fire
                elif armor3Rect.collidepoint(py.mouse.get_pos()):
                    characters[char].resistance = electric
    #time = py.time.get_ticks()
    if if_break == False:
        py.display.update()
    clock.tick(60)