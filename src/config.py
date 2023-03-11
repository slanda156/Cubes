import json
import glob
import pygame as py
from dataclasses import dataclass, asdict
import src.character
from src.logger import logger
from src.definition import RESOLUTIONS


@dataclass
class setting:
    """Classs for keeping track of settings"""
    resolution: list[int] = RESOLUTIONS[-1]
    fullscreen: bool = False
    logging: str = "INFO"
    fps: int = 60

    def getDict(self) -> dict:
        return asdict(self)

    def copy(self): #TODO Type hinting
        return setting(**self.getDict())

@dataclass
class screen:
    """Class for keepong track of current screen"""
    screen: str

    def get(self) -> str:
        """Get current screen"""
        return self.screen

    def set(self, screen: str) -> None:
        """Set current screen"""
        if type(screen) is not str:
            raise ValueError(f"Type should be string not {type(screen)}")
        self.screen = screen
        return None


with open("settings.json") as f:
    settingsDict:dict = json.load(f)
    try:
        settings = setting(**settingsDict)
    except ValueError:
        logger.error("Settings file wrongly formatted")

imageNames = glob.glob("images\\*.png")
images =  {}

for x in imageNames:
    x = x.split("\\")[1]
    images[x] = (py.image.load(f"images\\{x}"))

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

characters = src.character.characterList()

py.font.init()
fonts = {}
fonts["buttonFont"] = py.font.SysFont("Comic Sans Ms", 24)
fonts["titleFont"] = py.font.SysFont("Comic Sans Ms", 35)
fonts["title2Font"] = py.font.SysFont("Comic Sans Ms", 65)
fonts["itemFont"] = py.font.SysFont("Comic Sans Ms", 18)
fonts["effectFont"] = py.font.SysFont("Comic Sans Ms", 18)
