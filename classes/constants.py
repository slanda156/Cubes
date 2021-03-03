# Import modules
import json
import traceback as traceback
import glob
import time as ti
import random as ra
import logging
import pygame as py

# Sets the logging filter
t = ti.localtime()
startTime = ti.time()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.log", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load damage types
with open("classes\\damageTypes.json") as f:
    damageTypes = json.load(f)

version = "0.26"

# Defined resolutions
RESOLUTIONS = [
    [4096, 2160],
    [2960, 1440],
    [2560, 1440],
    [1920, 1080],
    [1280, 720],
    [960, 640],
    [800, 600]
]

# Define server
gameServers = []
mainServer = None

# Sets screen mode
screen = "main_menu"

# Configs
settings = {}

# Define Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTGREY = (169, 169, 169)
GREY = (100, 100, 100)
DARKGREY = (65, 65, 65)
RED = (255, 0, 0)
LIGHTRED = (230, 95, 57)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (253, 204, 85)
ERROCOLOR = (255, 0, 102)

# Define Fonts
py.font.init()

buttonFont = py.font.SysFont("Comic Sans Ms", 24)
titleFont = py.font.SysFont("Comic Sans Ms", 35)
title2Font = py.font.SysFont("Comic Sans Ms", 65)
itemFont = py.font.SysFont("Comic Sans Ms", 18)
effectFont = py.font.SysFont("Comic Sans Ms", 18)

# Define Textures
boss = {
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 1, 0, 1, 1, 0, 1, 0,
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
    0, 0, 1, 1, 1, 1, 0, 0,
    0, 0, 1, 0, 0, 1, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
}

baseSpeed = 150 # pixel/s
towerBaseCost = 10
enemyPower = 1

downTriangle = [py.Vector2(0, 0), py.Vector2(20, 0), py.Vector2(10, 10)]
upTriangle = [py.Vector2(0, 10), py.Vector2(20, 10), py.Vector2(10, 0)]

# Weapon Types
electric = damageTypes.get("electric")
fire = damageTypes.get("fire")
physical = damageTypes.get("physical")
laser = damageTypes.get("laser")
plasma = damageTypes.get("plasma")

# Load up sprits
imageNames = glob.glob("images\\*.png")
images =  {}

for x in imageNames:
    x = x.split("\\")[1]
    images[x] = (py.image.load(f"images\\{x}"))