from pygame import Surface
from src.equipment import weapon, armor

class character: #TODO Create character frame
    """Character frame"""
    ...

class player(character): #TODO Create player character
    """A playable character"""
    def __init__(self,
    pos: list[int],
    team: int,
    usedWeapon: weapon,
    usedArmor: armor,
    speed: int,
    gamesurf: Surface
    ):
        ...

    def addItem(self, item):
        ...
    
class enemy(character): #TODO Create enemy character
    """Enemy character"""
    ...

class characterList(list):
    def getPlayer(self) -> list[player]:
        """Return a list with all players"""
        players = []
        for p in self:
            if p.player:
                players.append(p)
        return players

    def empty(self) -> None:
        """Deletes the content of the list"""
        for i in range(len(self)-1):
            del self[i]
        return None

class projectil: #TODO Create projectils
    ...

class old_projectil: # TODO Move to new class
    def __init__(self, start, dierection, power, weapon, team, gamesurf):
        self.gamesurf = gamesurf
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
        newStart = self.start - offset
        newStart = (int(newStart[0]), int(newStart[1]))
        #self.offset.scale_to_length(self.weapon.speed/1000 * time) # TODO

        if self.weapon.type == plasma:
            py.draw.circle(self.gamesurf, self.weapon.color, (int(newStart[0]), int(newStart[1])), int(self.power/2))
        else:
            py.draw.line(self.gamesurf, self.weapon.color, newStart, (newStart + self.dierection), self.power*2)

        self.start += self.offset
        self.range -= self.offset.length()

class old_character: #TODO Move to new classes
    def __init__(self, pos, origine, team, usedWeapon, usedArmor, speed, towerCost, gamesurf, controlled=False):
        self.gamesurf = gamesurf
        self.controlled = controlled
        self.pos = py.Vector2(pos[0], pos[1])
        self.newPos = [0, 0]
        self.origine = origine
        self.destiny = None
        self.type = "player"
        self.shots = []
        self.weapon = usedWeapon
        self.armor = usedArmor
        self.team = team
        self.visibility = 1
        self.awareness = 1
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
        self.towerCost = towerCost
        self.towerUpgrades = []
        self.towerAccuracy = 1
        self.towerWeapon = weapons[findObjectInList(weapons, "rifle")]
        self.accuracy = 1

        self.inventory = []
        self.equipItem = None

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
        self.time = 0

        if self.armor.type == physical:
            self.movementSpeed = int(speed * 0.8)
        else:
            self.movementSpeed = int(speed)

    def draw(self, offset, time, lights, playerCharacter):
        self.time = time
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
            if x.type == electric:
                self.awareness = 0

            if x.duration <= 0:
                # Restore awareness
                if x.type == electric:
                    self.awareness = 1

                try:
                    del self.effect[self.effect.index(x)]
                except:
                    logger.warning("Effect not deletet")

        if self.controlled:
            self.target = py.mouse.get_pos() + offset

        else:
            target = playerCharacter

            if canSeeTarget(self, target):
                self.target = target
                if self.destiny is None:
                    self.destiny = self.target.pos

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

    def ai(self):
        if not checkList(self.effect, "shocked"):
            if self.cooldown <= 0 and isinstance(self.target, character):
                if calcDist(self.pos, self.target.pos) < self.weapon.range:
                    self.shoot()

            self.move()

    def getHit(self, hitWeapon):
        self.effectDuration = hitWeapon.effectDuration

        if hitWeapon.effect is not None:
            if checkList(self.effect, hitWeapon.effect):
                effectPos = self.effect.index(hitWeapon.effect)
                self.effect[effectPos].effectDuration = hitWeapon.effectDuration
                self.effect[effectPos].effectDamage = hitWeapon.effectDamage

            else:
                self.effect.append(effect(hitWeapon.type, hitWeapon.effectDuration, hitWeapon.damage/10, hitWeapon.color))

        if self.armor.type == hitWeapon.type:
            self.health -= hitWeapon.damage/2

        else:
            self.health -= hitWeapon.damage

    def healthBar(self):
        pos = self.newPos + py.Vector2(0, -20)

        py.draw.rect(self.gamesurf, GREY, (pos[0]-20, pos[1]-6, 40, 12))

        py.draw.rect(self.gamesurf, LIGHTGREY, (pos[0]-18, pos[1]-4, 36, 8))

        i = self.health / self.maxHealth

        if i > 1:
            i = 1

        py.draw.rect(self.gamesurf, RED, (pos[0]-18, pos[1]-4, int(36*i), 8))

    def shoot(self):
        if isinstance(self.target, py.Vector2):
            localTarget = self.target
        else:
            localTarget = self.target.pos

        dierection = py.Vector2(localTarget[0]-self.pos[0], localTarget[1]-self.pos[1])

        if self.weapon.type == fire:
            i = ra.randrange(3, 5)

            while i <= 5:
                newDierection = dierection + offsetTrajectory(dierection, 100 * self.accuracy)
                self.shots.append(projectile(self.pos[:], newDierection, self.weapon.power, self.weapon, self.team, self.gamesurf))
                i += 1

        elif self.weapon.type == electric:
            dierection += offsetTrajectory(dierection, 20 * self.accuracy)
            self.shots.append(projectile(self.pos[:], dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        elif self.weapon.type == physical:
            dierection += offsetTrajectory(dierection, 5 * self.accuracy)
            self.shots.append(projectile(self.pos[:], dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        elif self.weapon.type == laser:
            dierection += offsetTrajectory(dierection, 2 * self.accuracy)
            self.shots.append(projectile(self.pos[:], dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        elif self.weapon.type == plasma:
            dierection += offsetTrajectory(dierection, 20 * self.accuracy)
            self.shots.append(projectile(self.pos[:], dierection, self.weapon.power, self.weapon, self.team, self.gamesurf))

        self.cooldown = self.maxCooldown

    def spawnTower(self):
        self.resources -= self.towerCost
        self.towerCost += towerBaseCost

        self.towers.append(tower((self.pos[0], self.pos[1]-40), self.team, self.towerWeapon, self.level, self.towerAccuracy))

    def addItem(self, item):
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

    def useItem(self, pos=0):
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

    def changeItem(self, scroll):
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
