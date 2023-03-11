import json
from typing import Union
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
    def getFromName(self, name: str) -> Union[list[item], None]:
        """Return the first entry with the given name"""
        for e in self:
            if e.name == name:
                return e
        return None


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


with open("configs\\weapons.json") as f:
    weaponsDir = json.load(f)
    weapons = equipmentList()
    for w in weaponsDir.values():
        eff = []
        for i in range(len(w["effects"]) - 1):
            eff.append(effect(w["effects"][i], w["effectModifier"][i]))
        weapons.append(weapon(
            w["name"],
            w["displayName"],
            w["damage"],
            w["range"],
            w["speed"],
            w["firingSpeed"],
            w["power"],
            w["color"],
            w["type"],
            eff
        ))


with open("configs\\items.json") as f:
    itemsDir = json.load(f)
    items = itemList()
    for i in itemsDir.values():
        items.append(item(*i))


with open("configs\\armors.json") as f:
    armorsDir = json.load(f)
    armors = armorList()
    for a in armorsDir.values():
        armors.append(armor(**a))
