import pygame as py
import random as ra
from typing import Union
from src.logger import logger
from src.definition import COLORS
from src.equipment import weapon, armor
from src.effects import damageTypes, effect, effectList
from src.functions import calcDist
from src.buildings import tower

class character: #TODO Create character frame
    """Character frame"""
    def __init__(self, pos: list[int], team: int, weapon: weapon, armor: armor, speed: int, gamesurf: py.Surface):
        self.pos = py.Vector2(pos[0], pos[1])
        self.team = team
        self.weapon = weapon
        self.armor = armor
        self.speed = speed
        self.gamesurf = gamesurf

        self.shots = []
        self.cooldown = 0.1
        self.maxCooldown = self.weapon.firingSpeed
        self.level = 1
        self.xp = 0
        self.resources = 0

        self.maxCharge = 200
        self.charge = 0

        if self.armor.type == damageTypes["physical"]:
            self.maxHealth = float(10 * self.level * 2)
        else:
            self.maxHealth = float(10 * self.level)

        self.health = self.maxHealth
        self.maxBoost = 100
        self.boost = self.maxBoost

        self.effects = effectList()

        self.radius = 20

        if self.armor.type == damageTypes["physical"]:
            self.movementSpeed = int(speed * 0.8)
        else:
            self.movementSpeed = int(speed)

    def draw(self, offset, time, playerCharacter): #TODO Refactor
        self.time = time

        self.newPos = self.pos - offset
        self.newPos = (int(self.newPos[0]), int(self.newPos[1]))

        self.maxCooldown = self.weapon.reloadTime / 100

        if self.armor.type == damageTypes.get("physical"):
            self.maxHealth = float(10 * self.level * 2)
        else:
            self.maxHealth = float(10 * self.level)

        if self.boost > self.maxBoost:
            self.boost = self.maxBoost

        if self.charge < self.maxCharge:
            self.charge += self.time*10
        else:
            self.charge = self.maxCharge

        if self.xp >= (self.level * 100):
            self.xp = 0
            self.level += 1

        for x in self.effect:
            if x.type == self.armor.type:
                self.health -= (x.damage*self.time)*0.33
            else:
                self.health -= x.damage*self.time

            # Change awarness
            if x.type == damageTypes.get("electric"):
                self.awareness = 0

            if x.duration <= 0:
                # Restore awareness
                if x.type == damageTypes.get("electric"):
                    self.awareness = 1

                try:
                    del self.effect[self.effect.index(x)]
                except:
                    logger.warning("Effect not deletet")

        if self.controlled:
            self.target = py.mouse.get_pos() + offset

        else:
            target = playerCharacter

            self.ai()

        for x in self.effect:
            if x.duration > 0:
                x.duration -= self.time

        py.draw.circle(self.gamesurf, (200, 200, 200), self.newPos, self.radius)

        if isinstance(self.target, py.Vector2):
            target = self.target
        else:
            target = self.target.pos

        lookDir = py.Vector2(target[0]-self.pos[0], target[1]-self.pos[1])
        try:
            lookDir.scale_to_length(30)
        except:
            logger.warning("Cannot scale a vector with zero length")

        py.draw.line(self.gamesurf, self.weapon.color, self.newPos, (self.newPos + lookDir), int(self.radius/4))

        py.draw.circle(self.gamesurf, self.armor.color, self.newPos, int(self.radius/3))

        self.cooldown -= self.time

    def shoot(self): #TODO Refactor
        if isinstance(self.target, py.Vector2):
            localTarget = self.target
        else:
            localTarget = self.target.pos

        dierection = py.Vector2(localTarget[0]-self.pos[0], localTarget[1]-self.pos[1])

        if self.weapon.type == damageTypes.get("fire"):
            i = ra.randrange(3, 5)

            while i <= 5:
                newDierection = dierection + randomizeVector(dierection, 100 * self.accuracy)
                self.shots.append(projectile(self.pos[:], newDierection, self.weapon.power, self.weapon, self.team, self.gamesurf))
                i += 1

        elif self.weapon.type == damageTypes.get("electric"):
            dierection += randomizeVector(dierection, 20 * self.accuracy)
            self.shots.append(projectile(self.pos[:], dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        elif self.weapon.type == damageTypes.get("physical"):
            dierection += randomizeVector(dierection, 5 * self.accuracy)
            self.shots.append(projectile(self.pos[:], dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        elif self.weapon.type == damageTypes.get("laser"):
            dierection += randomizeVector(dierection, 2 * self.accuracy)
            self.shots.append(projectile(self.pos[:], dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        elif self.weapon.type == damageTypes.get("plasma"):
            dierection += randomizeVector(dierection, 20 * self.accuracy)
            self.shots.append(projectile(self.pos[:], dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        self.cooldown = self.maxCooldown

    def move(self): #TODO Refactor
        if self.destiny is not None:
            x = int(self.destiny[0])
            y = int(self.destiny[1])
            self.destiny = py.Vector2(x,y)

            if calcDist(self.pos, self.destiny) > 10:
                localDir = py.Vector2(self.destiny[0]-self.pos[0], self.destiny[1]-self.pos[1])

                try:
                    localDir.scale_to_length(int(self.movementSpeed * self.time))
                except:
                    logger.warning("Cannot scale a vector with zero length")

                if calcDist(self.pos, self.destiny) > (self.weapon.range/2):
                    if self.boost > 0 and calcDist(self.pos, self.destiny) > self.weapon.range:
                        localDir.scale_to_length(int((self.movementSpeed * 2) * self.time))
                        self.boost -= 20
                    else:
                        self.boost += 10

                    self.pos[0] += int(localDir[0])
                    self.pos[1] += int(localDir[1])

                else:
                    if self.boost > 0 and calcDist(self.pos, self.destiny) < (self.weapon.range/3):
                        localDir.scale_to_length(int((self.movementSpeed * 2) * self.time))
                        self.boost -= 20
                    else:
                        self.boost += 10

                    self.pos[0] -= int(localDir[0])
                    self.pos[1] -= int(localDir[1])
            else:
                self.destiny = None
        else:
            self.idle()

    def healthBar(self): #TODO Refactor
        pos = self.newPos + py.Vector2(0, -20)

        py.draw.rect(self.gamesurf, COLORS["GREY"], (pos[0]-20, pos[1]-6, 40, 12))

        py.draw.rect(self.gamesurf, COLORS["LIGHTGREY"], (pos[0]-18, pos[1]-4, 36, 8))

        i = self.health / self.maxHealth

        if i > 1:
            i = 1

        py.draw.rect(self.gamesurf, COLORS["RED"], (pos[0]-18, pos[1]-4, int(36*i), 8))

    def getHit(self, hitWeapon): #TODO Refactor
        self.effectDuration = hitWeapon.effectDuration

        if hitWeapon.effect is not None:
            if self.effects.checkForName(hitWeapon.effect):
                effectPos = self.effect.index(hitWeapon.effect)
                self.effect[effectPos].effectDuration = hitWeapon.effectDuration
                self.effect[effectPos].effectDamage = hitWeapon.effectDamage

            else:
                self.effect.append(effect(hitWeapon.type, hitWeapon.effectDuration, hitWeapon.damage/10, hitWeapon.color))

        if self.armor.type == hitWeapon.type:
            self.health -= hitWeapon.damage/2

        else:
            self.health -= hitWeapon.damage


class player(character): #TODO Create player character
    """A playable character"""
    def __init__(self,
        pos: list[int],
        team: int,
        weapon: weapon,
        armor: armor,
        speed: int,
        gamesurf: py.Surface
    ):
        super().__init__(pos, team, weapon, armor, speed, gamesurf)
        self.kills = 0
        self.inventory = []
        self.equipItem = None

    def draw(self, offset, time, playerCharacter): #TODO Create draw function
        super().draw(offset, time, playerCharacter)

    def spawnTower(self): #TODO Refactor
        self.resources -= self.towerCost
        # self.towerCost += towerBaseCost

        self.towers.append(tower((self.pos[0], self.pos[1]-40), self.team, self.towerWeapon, self.level, self.towerAccuracy))

    def addItem(self, item): #TODO Refactor
        try:
            index = self.inventory.index(item)
            number = self.inventory[index].number
            item.number = number + 1
        except:
            pass
        finally:
            self.inventory.append(item)
            if len(self.inventory) == 1:
                self.equipItem = self.inventory[0]

    def useItem(self, pos=0): #TODO Refactor
        if pos == 0:
            index = self.inventory.index(self.equipItem)

            if self.equipItem.category == "healing":
                self.health += self.equipItem.healing
                if self.health > self.maxHealth:
                    self.health = self.maxHealth

            self.equipItem.uses -= 1
            if self.equipItem.uses <= 0:
                del self.inventory[index]
                if len(self.inventory) > 0:
                    self.equipItem = self.inventory[0]
                else:
                    self.equipItem = None
            else:
                self.inventory[index] = self.equipItem

        elif pos > 0:
            index = pos - 1

            if self.inventory[index].category == "healing":
                self.health += self.inventory[index].healing
                if self.health > self.maxHealth:
                    self.health = self.maxHealth

            self.inventory[index].uses -= 1
            if self.inventory[index].uses <= 0:
                del self.inventory[index]

    def chaneeItem(self, scroll): #TODO Refactor
        if len(self.inventory) > 1:
            index = self.inventory.index(self.equipItem) + scroll
            if index > len(self.inventory)-1:
                index = index - (len(self.inventory)-1)
            elif index < 0:
                index = len(self.inventory) + index
            self.equipItem = self.inventory[index]

        elif len(self.inventory) > 0:
            self.equipItem = self.inventory[0]

        else:
            self.equipItem = None

class enemy(character): #TODO Create enemy character
    """Enemy character"""
    def draw(self, offset, time, playerCharacter): #TODO Create draw function
        super().draw(offset, time, playerCharacter)

    def idle(self):
        # Check how far away the origine is
        if calcDist(self.pos, self.origine.pos) >= 250:
            # Set origine as target
            self.target = self.origine

        elif calcDist(self.pos ,self.origine.pos) < 250:
            # Get x & y cordinates
            a = self.pos[0]
            b = self.pos[1]
            # Generate vector out of position
            target = py.Vector2(a, b)
            # Rotate vector
            target = target.rotate(1)
            # Set current destiny to target
            self.destiny = target
            # Move to target
            self.move()

    def ai(self):
        if not self.effects.checkForName("shocked"):
            if self.cooldown <= 0 and isinstance(self.target, character):
                if calcDist(self.pos, self.target.pos) < self.weapon.range:
                    self.shoot()

            self.move()


class characterList(list):
    def getPlayer(self) -> Union[list[player], player]:
        """Return a list with all players or the only player"""
        players = []
        for p in self:
            if type(p) is player:
                players.append(p)
        
        return players if len(players) > 1 else players[0]


class projectile: # TODO Refactor projectile
    def __init__(self, start, dierection, power, weapon, team, gamesurf):
        self.gamesurf = gamesurf
        self.start = start
        self.dierection = dierection
        self.power = int(power)
        self.team = team
        self.weapon = weapon
        self.range = weapon.range

        if self.power != 0:
            if self.weapon.type == damageTypes.get("physical"):
                self.dierection.scale_to_length(self.power*4)
            elif self.weapon.type == damageTypes.get("laser"):
                self.dierection.scale_to_length(self.power*6)
            else:
                self.dierection.scale_to_length(self.power)

        self.offset = self.dierection

    def draw(self, offset):
        newStart = self.start - offset
        newStart = (int(newStart[0]), int(newStart[1]))
        #self.offset.scale_to_length(self.weapon.speed/1000 * time) # TODO Fix bug

        if self.weapon.type == damageTypes.get("plasma"):
            py.draw.circle(self.gamesurf, self.weapon.color, (int(newStart[0]), int(newStart[1])), int(self.power/2))
        else:
            py.draw.line(self.gamesurf, self.weapon.color, newStart, (newStart + self.dierection), self.power*2)

        self.start += self.offset
        self.range -= self.offset.length()


def randomizeVector(start: py.Vector2, splatter: int) -> py.Vector2:
    """Randomize pygame.Vector2 by splatter"""
    start[0] = int(start[0])
    start[1] = int(start[1])
    return py.Vector2(ra.randint(start[0]-splatter, start[0]+splatter), ra.randint(start[1]-splatter, start[1]+splatter))


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


def checkHits(projectiles, objects, characters):
    for x in projectiles:
        for y in objects:
            if x.team != y.team:
                if y.type == "tower" and checkRectangle(py.Rect(y.pos[0], y.pos[1], y.size[0], y.size[1]), x):
                    y.getHit(x.weapon)
                elif y.type == "player" and checkCircle(y, x, y.radius):
                    y.getHit(x.weapon)
                    if y.health <= 0:
                        if x.team == 0:
                            i = characters.getPlayer()
                            i.xp += (i.level*20)
                            i.resources += ((y.level/3)*20)

                    try:
                        del projectiles[projectiles.index(x)]
                    except IndexError:
                        logger.warning("Projectile not deletet")


def getNearestCharacter(start, characters):
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


def getNearestPlayer(start, characters):
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


def getNearestEnemie(start, characters):
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
