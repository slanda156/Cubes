from dataclasses import dataclass
from src.effects import damageType, effect

@dataclass
class weapon:
    name: str
    displayName: str
    damage: float
    range: int
    speed: int
    firingSpeed: int
    power: int
    color: list[int]
    type: damageType
    effects: list[effect]

@dataclass
class armor:
    name: str
    displayName: str
    type: damageType
    color: list[int]

@dataclass
class item:
    name: str
    displayName: str
    type: str
    uses: int
    arg: dict

class equipmentList(list):
    def getFromName(self, name:str) -> list[item]:
        """Return the first entry with the given name"""
        for e in self:
            if e.name == name:
                return e

class armorList(equipmentList):
    def getFromType(self, type) -> list:
        """Returns a list with the given type"""
        tempList = []
        for a in self:
            if a.resType == type:
                tempList.append(a)
        return tempList

class itemList(equipmentList):
    ...
