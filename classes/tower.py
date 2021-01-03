# Import needed modules
import pygame as py

class tower:
    def __init__(self, pos, team, weapon, level, accuracy):
        self.team = team
        self.type = "tower"
        self.shots = []
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
                except:
                    logger.warning("Effect not deletet")

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
        dierection = py.Vector2(target[0]-self.pos[0], target[1]-self.pos[1])

        if weapon.type == fire:
            i = ra.randrange(3, 5)

            while i <= 5:
                newDierection = dierection + offsetTrajectory(dierection, 100 * self.accuracy)
                projectiles.append(projectile(self.pos, newDierection, self.weapon.power, self.weapon, self.team))
                i += 1

        elif weapon.type == electric:
            dierection += offsetTrajectory(dierection, 20 * self.accuracy)
            projectiles.append(projectile(self.pos, dierection, self.weapon.power, self.weapon, self.team))

        elif weapon.type == physical:
            dierection += offsetTrajectory(dierection, 5 * self.accuracy)
            projectiles.append(projectile(self.pos, dierection, self.weapon.power, self.weapon, self.team))

        elif weapon.type == laser:
            dierection += offsetTrajectory(dierection, 2 * self.accuracy)
            projectiles.append(projectile(self.pos, dierection, self.weapon.power, self.weapon, self.team))

        elif weapon.type == plasma:
            dierection += offsetTrajectory(dierection, 20 * self.accuracy)
            projectiles.append(projectile(self.pos, dierection, self.weapon.power, self.weapon, self.team))
        
        self.cooldown = self.maxCooldown

    def healthBar(self):
        pos = self.newPos + py.Vector2(0, -20)

        py.draw.rect(gamesurf, GREY, (pos[0]-20, pos[1]-6, 40, 12))

        py.draw.rect(gamesurf, LIGHTGREY, (pos[0]-18, pos[1]-4, 36, 8))

        i = self.health / self.maxHealth

        py.draw.rect(gamesurf, RED, (pos[0]-18, pos[1]-4, int(36*i), 8))