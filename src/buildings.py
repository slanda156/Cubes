from pygame import Surface

class nest: #TODO Refactor nests
    def __init__(self, pos: list[int], team: int, gamesurf: Surface):
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

class heart: #TODO Refactor hearts
    def __init__(self, pos, team, sprit, gamesurf):
        self.gamesurf = gamesurf
        self.pos = pos
        self.team = team
        self.sprit = sprit
        self.maxCooldown = 120
        self.cooldown = self.maxCooldown

    def atack(self):
        ...

    def draw(self, offset, time):
        newPos = self.pos - offset
        newPos = (int(newPos[0]), int(newPos[1]))

        # Draw sprit
        self.gamesurf.blit(self.sprit, newPos)

        self.cooldown -= time

        if self.cooldown <= 0:
            self.cooldown = 0

class spawnPoint: #TODO Refactor spawnPoints
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

class tower: #TODO Refactor towers
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

class barrier: #TODO Create barriers
    ...
