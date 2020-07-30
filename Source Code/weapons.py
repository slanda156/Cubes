import logging
from damageTypes import damageTypes

weaponNum = 6

weapons = []

def initWeapon():
    logging.info("Loading weapons")
    for i in range(weaponNum):
        weapons.append(weapon(i))

class weapon:
    def __init__(self, index):
        self.name = "None"
        self.displayName = "None"
        self.damage = 0
        self.range = 1
        self.speed = 1
        self.reloadTime = 1
        self.power = 1
        self.color = (255, 0, 102)
        self.type = None
        self.effect = None
        self.effectDuration = 0
        if index == 0:
            self.sniper()
        elif index == 1:
            self.rifle()
        elif index == 2:
            self.flamethrower()
        elif index == 3:
            self.plasmaCanone()
        elif index == 4:
            self.plasmaRifle()
        elif index == 5:
            self.laserRifle()

    def sniper(self):
        self.name = "sniper"
        self.displayName = "Sniper"
        self.damage = 10
        self.range = 1000
        self.speed = 350
        self.firingSpeed = 330
        self.magSize = 5
        self.reloadTime = 330
        self.power = 3
        self.color = (100, 100, 100)
        self.type = damageTypes.get("physical")
        self.effect = None
        self.effectDamage = 0
        self.effectDuration = 0

    def rifle(self):
        self.name = "rifle"
        self.displayName = "Rifle"
        self.damage = 2
        self.range = 650
        self.speed = 200
        self.firingSpeed = 40
        self.magSize = 30
        self.reloadTime = 40
        self.power = 2
        self.color = (100, 100, 100)
        self.type = damageTypes.get("physical")
        self.effect = None
        self.effectDamage = 0
        self.effectDuration = 0

    def flamethrower(self):
        self.name = "flamethrower"
        self.displayName = "Flamethrower"
        self.damage = 0.5
        self.range = 300
        self.speed = 20
        self.firingSpeed = 10
        self.magSize = 100
        self.reloadTime = 10
        self.power = 6
        self.color = (252, 93, 25)
        self.type = damageTypes.get("fire")
        self.effect = "burning"
        self.effectDamage = 0.5
        self.effectDuration = 10

    def plasmaCanone(self):
        self.name = "plasmaCanone"
        self.displayName = "Plasma Canone"
        self.damage = 10
        self.range = 500
        self.speed = 200
        self.firingSpeed = 300
        self.magSize = 8
        self.reloadTime = 300
        self.power = 20
        self.color = (64, 56, 201)
        self.type = damageTypes.get("plasma")
        self.effect = "shocked"
        self.effectDamage = 1
        self.effectDuration = 3

    def plasmaRifle(self):
        self.name = "plasmaRifle"
        self.displayName = "Plasma Rifle"
        self.damage = 2
        self.range = 500
        self.speed = 300
        self.firingSpeed = 20
        self.magSize = 25
        self.reloadTime = 20
        self.power = 10
        self.color = (64, 56, 201)
        self.type = damageTypes.get("plasma")
        self.effect = "shocked"
        self.effectDamage = 1
        self.effectDuration = 2

    def laserRifle(self):
        self.name = "laserRifle"
        self.displayName = "Laser Rifle"
        self.damage = 4
        self.range = 600
        self.speed = 400
        self.firingSpeed = 80
        self.magSize = 20
        self.reloadTime = 80
        self.power = 5
        self.color = (255, 87, 196)
        self.type = damageTypes.get("laser")
        self.effect = "burning"
        self.effectDamage = 1
        self.effectDuration = 2
