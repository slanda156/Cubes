# Import needed modules
import pygame as py
from classes.weapons import *
from classes.functions import *
from classes.item import *
from classes.constants import *
from classes.projectile import *

class character:
    def __init__(self, pos, origine, team, weapon, armor, speed, towerBaseCost, gamesurf, controlled=False):
        self.gamesurf = gamesurf
        self.controlled = controlled
        self.pos = py.Vector2(pos[0], pos[1])
        self.origine = origine
        self.destiny = None
        self.type = "player"
        self.shots = []
        self.weapon = weapon
        self.armor = armor
        self.team = team
        self.visibility = 1
        self.cooldown = 0.1
        self.maxCooldown = self.weapon.reloadTime / 100
        self.target = self.origine
        self.level = 1
        self.xp = 0
        self.visualRange = 500
        self.resources = 0
        self.upgrades = []
        self.maxCharge = 200
        self.charge = 0
        self.towers = []
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

    def draw(self, offset, time, lights):
        # Get current brightness
        lamps = getLights(self.pos, lights)
        b = 1
        for x in lamps:
            distance = calcDist(self.pos, x.pos)
            brightness = x.getBrightnes(distance)
            b *= brightness
        # Calc current visiblity
        self.visibility = 1 * b

        self.newPos = self.pos - offset
        self.newPos = (int(self.newPos[0]), int(self.newPos[1]))

        self.maxCooldown = self.weapon.reloadTime / 100

        if self.armor.type == physical:
            self.maxHealth = float(10 * self.level * 2)
        else:
            self.maxHealth = float(10 * self.level)

        if self.boost > self.maxBoost:
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
                self.health -= (x.damage*time)*0.33
            else:
                self.health -= x.damage*time

            if x.duration <= 0:
                try:
                    del self.effect[self.effect.index(x)]
                except:
                    logger.warning("Effect not deletet")

        if self.controlled:
            self.target = py.mouse.get_pos() + offset
            
        else:
            target = characters[findPlayerChar()]

            if canSeeTarget(self, target):
                self.target = target
                if self.destiny is None:
                    self.destiny = self.target.pos

            self.ai()

        for x in self.effect:
            if x.duration > 0:
                x.duration -= time

        py.draw.circle(self.gamesurf, (200, 200, 200), self.newPos, self.radius)

        if type(self.target) is py.Vector2:
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

        if target is not None:
            pos = target - offset
            newpos = (int(pos[0]), int(pos[1]))
            py.draw.circle(self.gamesurf, ERROCOLOR, newpos, 20)

        self.cooldown -= time

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

    def move(self):
        if self.destiny is not None:
            x = int(self.destiny[0])
            y = int(self.destiny[1])
            self.destiny = py.Vector2(x,y)

            if calcDist(self.pos, self.destiny) > 10:
                localDir = py.Vector2(self.destiny[0]-self.pos[0], self.destiny[1]-self.pos[1])

                try:
                    localDir.scale_to_length(int(self.movementSpeed * time))
                except:
                    logger.warning("Cannot scale a vector with zero length")

                if calcDist(self.pos, self.destiny) > (self.weapon.range/2):
                    if self.boost > 0 and calcDist(self.pos, self.destiny) > self.weapon.range:
                        localDir.scale_to_length(int((self.movementSpeed * 2) * time))
                        self.boost -= 20
                    else:
                        self.boost += 10

                    self.pos[0] += int(localDir[0])
                    self.pos[1] += int(localDir[1])

                else:
                    if self.boost > 0 and calcDist(self.pos, self.destiny) < (self.weapon.range/3):
                        localDir.scale_to_length(int((self.movementSpeed * 2) * time))
                        self.boost -= 20
                    else:
                        self.boost += 10

                    self.pos[0] -= int(localDir[0])
                    self.pos[1] -= int(localDir[1])
            else:
                self.destiny = None
        else:
            pass
            self.idle()

    def ai(self):
        if not checkList(self.effect, "shocked"):
            if self.cooldown <= 0 and type(self.target) == character:
                if calcDist(self.pos, self.target.pos) < self.weapon.range:
                    self.shoot()

            self.move()

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

        py.draw.rect(self.gamesurf, GREY, (pos[0]-20, pos[1]-6, 40, 12))

        py.draw.rect(self.gamesurf, LIGHTGREY, (pos[0]-18, pos[1]-4, 36, 8))

        i = self.health / self.maxHealth

        if i > 1:
            i = 1

        py.draw.rect(self.gamesurf, RED, (pos[0]-18, pos[1]-4, int(36*i), 8))

    def shoot(self):
        if type(self.target) is py.Vector2:
            localTarget = self.target
        else:
            localTarget = self.target.pos
        
        dierection = py.Vector2(localTarget[0]-self.pos[0], localTarget[1]-self.pos[1])

        if self.weapon.type == fire:
            i = ra.randrange(3, 5)

            while i <= 5:
                newDierection = dierection + offsetTrajectory(dierection, 100 * self.accuracy)
                self.shots.append(projectile(self.pos, newDierection, self.weapon.power, self.weapon, self.team, self.gamesurf))
                i += 1

        elif self.weapon.type == electric:
            dierection += offsetTrajectory(dierection, 20 * self.accuracy)
            self.shots.append(projectile(self.pos, dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        elif self.weapon.type == physical:
            dierection += offsetTrajectory(dierection, 5 * self.accuracy)
            self.shots.append(projectile(self.pos, dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        elif self.weapon.type == laser:
            dierection += offsetTrajectory(dierection, 2 * self.accuracy)
            self.shots.append(projectile(self.pos, dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        elif self.weapon.type == plasma:
            dierection += offsetTrajectory(dierection, 20 * self.accuracy)
            self.shots.append(projectile(self.pos, dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        self.cooldown = self.maxCooldown

    def spawnTower():
        self.resources -= self.towerCost
        self.towerCost += towerBaseCost

        self.towers.append(tower((pos[0], pos[1]-40), self.team, self.towerWeapon, self.level, self.towerAccuracy))