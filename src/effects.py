import json
from dataclasses import dataclass

@dataclass
class damageType:
    type: int = 0
    name: str = "physical"

class effect: #TODO Refactor effect
    def __init__(self, name, modifier):
        self.modifier = modifier
        self.name = name
        self.displayName = ""
        self.damage = 0
        self.duration = 0

class effectList(list):
    def getFromName(self, name: str) -> list:
        """Return a list with all elements with the same name"""
        tempList = effectList()
        for e in self:
            if e.name == name:
                tempList.append(e)
        return tempList

    def checkForName(self, effect: effect, strict: bool = False) -> bool:
        """
        Check if given effect is in list
        If strict=True check for same damage
        """
        for e in self:
            if strict and e.name is effect.name and e.damage is effect.name:
                return True
            elif not strict and e.name is effect.name:
                return True
            return False


damageTypes = {}
with open("configs\\damageTypes.json") as f:
    damageTypesDir = json.load(f)
    for d in damageTypesDir.items():
        damageTypes[d[0]] = damageType(*d)
