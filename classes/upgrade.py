# Importing modules
from classes.constants import logger

upgradeNum = 6
upgrades = []

class upgrade:
    def __init__(self, index):
        self.name = "None"
        self.displayName = "None"
        self.type = None
        self.armorType = None
        self.damage = 0
        self.range = 1
        self.speed = 1
        self.reloadTime = 1
        self.power = 1
        self.color = (255, 0, 102)
        self.effect = None
        self.effectDuration = 0

        if index == 0:
            self.laserRifle()

    def laserRifle(self):
        self.name = "laserRifle"
        self.displayName = "Laser Rifle Upgrade"
        self.type = "weapon"
        self.damage = 0
        self.range = 1
        self.speed = 1
        self.reloadTime = 1
        self.power = 1
        self.color = (255, 0, 102)
        self.effect = None
        self.effectDuration = 0

logger.info("Loading upgrades")
for i in range(upgradeNum):
    upgrades.append(upgrade(i))