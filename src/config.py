import json
import glob
import pygame as py
from dataclasses import dataclass, asdict

from src.logger import logger
from src.effects import damageType
from src.equipment import (
    weapon,
    equipmentList,
    armor,
    armorList,
    item,
    itemList
)
from src.character import characterList
from src.effects import effect

VERSION = "0.25"

RESOLUTIONS = (
    (4096, 2160),
    (2960, 1440),
    (2560, 1440),
    (1920, 1080),
    (1280, 720),
    (960, 640),
    (800, 600)
)

colors = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "LIGHTGREY": (169, 169, 169),
    "GREY": (100, 100, 100),
    "DARKGREY": (65, 65, 65),
    "LIGHTRED": (230, 95, 57),
    "RED": (255, 0, 0),
    "BLUE": (0, 0, 255),
    "GREEN": (0, 255, 0),
    "ORANGE": (253, 204, 85),
    "ERRCOLOR": (255, 0, 102)
}

@dataclass
class setting:
    """Classs for keeping track of settings"""
    resolution: list[int] = RESOLUTIONS[-1]
    fullscreen: bool = False
    logging: str = "INFO"

    def getDict(self) -> dict:
        return asdict(self)

with open("settings.json") as f:
    settingsDict:dict = json.load(f)
    try:
        settings = setting(**settingsDict)
    except ValueError:
        logger.error("Settings file wrongly formatted")

damageTypes = {}
with open("configs\\damageTypes.json") as f:
    damageTypesDir = json.load(f)
    for d in damageTypesDir.items():
        damageTypes[d[0]] = damageType(*d)
    

imageNames = glob.glob("images\\*.png")
images =  {}

for x in imageNames:
    x = x.split("\\")[1]
    images[x] = (py.image.load(f"images\\{x}"))

with open("configs\\weapons.json") as f:
    weaponsDir = json.load(f)
    weapons = equipmentList()
    for w in weaponsDir.values():
        eff = []
        for i in range(len(w["effects"])-1):
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

with open("configs\\armors.json") as f:
    armorsDir = json.load(f)
    armors = armorList()
    for a in armorsDir.values():
        armors.append(armor(**a))

with open("configs\\items.json") as f:
    itemsDir = json.load(f)
    items = itemList()
    for i in itemsDir.values():
        items.append(item(*i))

logger.setLevel(settings.logging)

WINDOWWIDTH = settings.resolution[0]
WINDOWHEIGHT = settings.resolution[1]

if settings.fullscreen:
    window = py.display.Info()
    WINDOWWIDTH = window.current_w
    WINDOWHEIGHT = window.current_h
    gamesurf = py.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), py.FULLSCREEN)

else:
    gamesurf = py.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

baseSpeed = 150 # pixel/s
towerBaseCost = 10
enemyPower = 1

characters = characterList()

py.font.init()
buttonFont = py.font.SysFont("Comic Sans Ms", 24)
titleFont = py.font.SysFont("Comic Sans Ms", 35)
title2Font = py.font.SysFont("Comic Sans Ms", 65)
itemFont = py.font.SysFont("Comic Sans Ms", 18)
effectFont = py.font.SysFont("Comic Sans Ms", 18)

downTriangle = [py.Vector2(0, 0), py.Vector2(20, 0), py.Vector2(10, 10)]
upTriangle = [py.Vector2(0, 10), py.Vector2(20, 10), py.Vector2(10, 0)]
