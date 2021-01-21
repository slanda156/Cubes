# Importing modules
from classes.constants import *

armorNum = 3
armors = []

class armor:
    def __init__(self, index):
        self.displayName = None
        self.color = (255, 0, 102)
        self.type = None
        if index == 0:
            self.physical()
        elif index == 1:
            self.fire()
        elif index == 2:
            self.electro()

    def physical(self):
        self.displayName = "Physical Armor"
        self.color = (100, 100, 100)
        self.type = damageTypes.get("physical")

    def fire(self):
        self.displayName = "Fire Armor"
        self.color = (252, 93, 25)
        self.type = damageTypes.get("fire")

    def electro(self):
        self.displayName = "Electric Armor"
        self.color = (64, 56, 201)
        self.type = damageTypes.get("electric")
        
logger.info("Loading armor")
for i in range(armorNum):
    armors.append(armor(i))