import pygame
import random as ra
import math

# Define the window
i = 0
cubeSize = 20
QUALITY = (16, 9)
WINDOWWIDTH = 1020
WINDOWHEIGHT = int((WINDOWWIDTH/QUALITY[0])*QUALITY[1])
while i < WINDOWHEIGHT:
    i += cubeSize
WINDOWHEIGHT = i

# Define Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (169,169,169)
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

dificulty = 5
oldPoints = 5
time = 0
oldTime = 0
bosse = 0

enemies = []
enemieShots = []
players = []
playerShots = []

# Define Classes
class healthBar:
    def __init__(self, boss, size, maxHealth):
        self.boss = boss
        self.size = size
        self.maxHealth = maxHealth
        self.height = 2
    def draw(self, x, y, health):
        self.x = x
        self.y = y+10+self.size
        if self.boss:
            self.newSize = (WINDOWWIDTH/2)*(health/self.maxHealth)
            pygame.draw.rect(gamesurf, WHITE, (WINDOWWIDTH/4, 20, WINDOWWIDTH/2, 40))
            pygame.draw.rect(gamesurf, GREY, ((WINDOWWIDTH/4)+5, 25, (WINDOWWIDTH/2)-10, 30))
            if self.newSize > 10:
                pygame.draw.rect(gamesurf, RED, ((WINDOWWIDTH/4)+5, 25, self.newSize-10, 30))
            return True
        else:
            self.newSize = self.size*(health/self.maxHealth)
            pygame.draw.rect(gamesurf, WHITE, (self.x, self.y, self.size, self.height+4))
            pygame.draw.rect(gamesurf, GREY, (self.x+2, self.y+2, self.size-4, self.height))
            if self.newSize > 4:
                pygame.draw.rect(gamesurf, RED, (self.x+2, self.y+2, self.newSize-4, self.height))

class new_projektile:
    def __init__(self, team, power, x1, y1, x2, y2):
        self.team = team
        self.power = power
        self.range = 0
        self.i = 1
        self.vector_pos = pygame.Vector2(x1,x2)
        self.vector_dir = pygame.Vector2((x2-x1),(y2-y1)).normalize()
        self.vector_off = self.vector_dir
        self.vector_dir.scale_to_length(50)

    def shooting(self):
        self.vector_off.scale_to_length(i)
        self.range += 1
        self.vector_pos += self.vector_off
        self.vector_a = self.vector_pos
        self.vector_b = self.vector_pos + self.vector_dir
        pygame.draw.line(gamesurf, GREEN, self.vector_a, self.vector_b, self.power)
        self.i += 10

class projektile:
    def __init__(self, team, power, range, direction, start):
        self.team = team
        self.range = range
        self.power = power
        self.start = start
        self.direction = direction
        self.i = 1
        self.vector_a = start
    def shooting(self):
        self.direction.scale_to_length(self.i)
        self.vector_a += self.direction
        self.direction.scale_to_length(int(math.log(self.power)*10))
        self.vector_b = self.vector_a + self.direction
        pygame.draw.line(gamesurf, GREEN, self.vector_a, self.vector_b, self.power)
        self.i += (self.power * 4)

class player:
    def __init__(self, x, y, size):
        self.team = 0
        self.size = size
        self.calcSize = self.size
        self.x_cord = x
        self.y_cord = y
        self.points = 0
        self.health = 100
        self.view = "right"
        self.healthBar = healthBar(False, self.calcSize, self.health)
    def move(self):
        if self.view == "up":
            self.y_cord -= cubeSize
        elif self.view == "down":
            self.y_cord += cubeSize
        elif self.view == "left":
            self.x_cord -= cubeSize
        elif self.view == "right":
            self.x_cord += cubeSize
        pygame.draw.rect(gamesurf, WHITE, (self.x_cord, self.y_cord, self.calcSize, self.calcSize))
    def checkFood(self, x, y, cubeSize):
        if self.x_cord == x:
            if self.y_cord == y:
                self.points += 1
                aFood.reset()
    def checkBorder(self):
        if self.x_cord < 0 or self.x_cord > WINDOWWIDTH:
            death()
        if self.y_cord < 0 or self.y_cord > WINDOWHEIGHT:
            death()
    def shoot(self):
        global playerShots
        self.mouse = pygame.mouse.get_pos()
        playerShots.append(projektile(1, 5, 10, pygame.Vector2((self.x_cord-cubeSize/2), (self.y_cord-cubeSize/2)), pygame.Vector2((self.mouse[0] - self.x_cord), self.mouse[1] - self.y_cord)))
    def getHit(self, power):
        self.health -= power
        if self.health <= 0:
            death()

class enemie:
    def __init__(self, size):
        global bosse
        self.team = 1
        global enemies
        self.size = size
        self.view = "right"
        self.difficulty = 1
        self.health = 100
        self.boss = False
        if enemies:
            if bosse == 0:
                if len(enemies) >= 5 and players[0].points >= 50:
                    self.boss = True
            elif bosse < 5:
                if players[0].points >= (50+(20*bosse)):
                    self.boss = True
        if len(enemies) <= 1:
            self.pos = 0
        else:
            self.pos = len(enemies)-1
        if self.boss:
            self.calcSize = self.size*(dificulty/2)
            if self.calcSize >= 100:
                self.calcSize = 100
        else:
            self.calcSize = self.size*(dificulty/10)
        self.x_cord = ra.randrange(0, (WINDOWWIDTH-self.calcSize), self.calcSize)
        self.y_cord = ra.randrange(0, (WINDOWHEIGHT-self.calcSize), self.calcSize)
        self.healthBar = healthBar(self.boss, self.calcSize, self.health)
    def move(self):
        if self.y_cord < players[0].y_cord:
            self.distanceY = players[0].y_cord - self.y_cord
        elif self.y_cord > players[0].y_cord:
            self.distanceY = self.y_cord - players[0].y_cord
        else:
            self.distanceY = 0
        if self.x_cord < players[0].x_cord:
            self.distanceX = players[0].x_cord - self.x_cord
        elif self.x_cord > players[0].x_cord:
            self.distanceX = self.x_cord - players[0].x_cord
        else:
            self.distanceX = 0
        self.vector_dist = pygame.Vector2(self.distanceX, self.distanceY)
        if self.vector_dist.magnitude() > 200:
            if self.distanceX < self.distanceY:
                if self.y_cord < players[0].y_cord:
                    self.y_cord += 10
                elif self.y_cord > players[0].y_cord:
                    self.y_cord -= 10
            elif self.distanceX > self.distanceY:
                if self.x_cord < players[0].x_cord:
                    self.x_cord += 10
                elif self.x_cord > players[0].x_cord:
                    self.x_cord -= 10
        elif self.vector_dist.magnitude() < 150:
            if self.distanceX < self.distanceY:
                if self.y_cord < players[0].y_cord:
                    self.y_cord -= 10
                elif self.y_cord > players[0].y_cord:
                    self.y_cord += 10
            elif self.distanceX > self.distanceY:
                if self.x_cord < players[0].x_cord:
                    self.x_cord -= 10
                elif self.x_cord > players[0].x_cord:
                    self.x_cord += 10
        pygame.draw.rect(gamesurf, RED, (self.x_cord, self.y_cord, int(self.calcSize), int(self.calcSize)))
    def shoot(self):
        global enemieShots
        #enemieShots.append(projektile(2, 5, 10, pygame.Vector2((self.x_cord-self.calcSize/2), (self.y_cord-self.calcSize/2)), pygame.Vector2(players[0].x_cord - self.x_cord, players[0].y_cord - self.y_cord)))
        print("test")
    def getHit(self, power):
        self.health -= power
        if self.health <= 0:
            global enemies
            for x in range((self.pos+1), (len(enemies)-1)):
                enemies[x].pos -= 1
            players[0].points = players[0].points + self.calcSize
            del enemies[self.pos]

class food:
    def __init__(self, size):
        self.size = size
        self.x_cord = 500
        self.y_cord = 500
    def draw(self):
        pygame.draw.rect(gamesurf, BLUE, (self.x_cord, self.y_cord, self.size, self.size))
    def reset(self):
        self.y_cord = ra.randrange(0, WINDOWHEIGHT, cubeSize)
        self.x_cord = ra.randrange(0, WINDOWWIDTH, cubeSize)

# AssigningClasses
players.append(player(100, 200, cubeSize))
aFood = food(cubeSize)

def death():
    saveHighscore(players[0].points)
    del players[0]
    players.append(player(100, 200, cubeSize))
    aFood.reset()
    global dificulty
    dificulty = 5
    global enemies
    global playerShots
    global enemieShots
    del playerShots
    playerShots = []
    del enemieShots
    enemieShots = []
    del enemies
    enemies = []
    spawnEnemie()

def sculpt(x, y, size, color, texture):
    line = 0
    a = 0
    x = x + (size/2)
    y = y + (size/2)
    sqare = math.sqrt(len(texture)-1)
    for i in texture:
        if a == sqare:
            line += 1
        if i == 1:
            return True
        elif i == 0:
            return False

def saveHighscore(points):
#    f = open('highscore.txt', 'r')
#    score = f.read()
#    f.close()
#    f = open('highscore.txt', 'w')
#    if int(score) < points:
#        f.write(str(points))
#    f.close()
    return True

def spawnEnemie():
    global enemies
    enemies.append(enemie(cubeSize))

def checkHits(shots, targets):
    for x in shots:
        for y in targets:
            z = pygame.Rect(y.x_cord, y.y_cord, y.calcSize, y.calcSize)
            if z.collidepoint(x.vector_a):
                if x.team != y.team:
                    y.getHit(x.power)

def checkLimits():
    if len(enemies) > 100:
        for x in range(100, (len(enemies)-1)):
            del enemies[x]

# Init Pygame and set the window
if pygame.get_init() == False:
    pygame.init()
gamesurf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Cubes')
pygame.event.clear()
clock = pygame.time.Clock()

font = pygame.font.Font(None, 32)
point_text = font.render(' ', True, WHITE, BLACK)
textRect1 = point_text.get_rect()
textRect1.center = (WINDOWWIDTH-30, 20)
spawnEnemie()

# Main Loop
while True:
    if if_break:
        break
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.display.quit()
                if_break = True
            elif event.key == pygame.K_w:
                players[0].view = "up"
            elif event.key == pygame.K_s:
                players[0].view = "down"
            elif event.key == pygame.K_a:
                players[0].view = "left"
            elif event.key == pygame.K_d:
                players[0].view = "right"
            elif event.key == pygame.K_SPACE:
                players[0].shoot()
            elif event.key == pygame.K_q:
                if len(enemies) > 0:
                    enemies[0].getHit(enemies[0].health)
            elif event.key == pygame.K_e:
                spawnEnemie()
    gamesurf.fill(BLACK)
    clock = pygame.time.Clock()
    point_text = font.render(str(players[0].points), True, WHITE, BLACK)
    gamesurf.blit(point_text, textRect1)
    checkHits(playerShots, enemies)
    checkHits(enemieShots, players)
    for x in players:
        x.move()
        x.healthBar.draw(x.x_cord, x.y_cord, x.health)
    for x in enemies:
        x.move()
        x.healthBar.draw(x.x_cord, x.y_cord, x.health)
        y = ra.randrange(0, 10, 1)
        if y > 8:
            x.shoot()
        if x.boss:
            bosse += 1
    for x in enemieShots:
        x.shooting()
    for x in playerShots:
         x.shooting()
    if len(enemieShots) <= 1:
        for x in range(0, (len(enemieShots)-1)):
            if enemieShots[x].range >= 10:
                del enemieShots[x]
    elif len(enemieShots) > 0:
        if enemieShots[0].range >= 10:
            del enemieShots[0]
    if len(playerShots) <= 1:
        for x in range(0, (len(playerShots)-1)):
            if playerShots[x].range >= 10:
                del playerShots[x]
    elif len(playerShots) > 0:
        if playerShots[0].range >= 10:
            del playerShots[0]
    (sculpt(10,10,10,RED,boss))
    checkLimits()
    aFood.draw()
    players[0].checkFood(aFood.x_cord, aFood.y_cord, cubeSize)
    clock.tick(10)
    players[0].checkBorder()
    time = pygame.time.get_ticks()
    if len(enemies) < 30:
        if time >= oldTime:
            spawnEnemie()
            oldTime = time + 5000
    if dificulty < 30:
        if players[0].points >= oldPoints:
            oldPoints += 5
            dificulty += 1
    if if_break == False:
        pygame.display.update()