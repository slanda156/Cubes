import json
import traceback
import random as ra
import pygame as py

from src.logger import logger
from src.config import (
    settings,
    colors,
    gamesurf,
    WINDOWWIDTH,
    WINDOWHEIGHT,
    weapons,
    armors,
    items,
    characters,
    baseSpeed
)
# from src.gui import icon, iconAndText, button, settingField
from src.character import player
from src.buildings import nest

def main():
    if not py.get_init():
        py.init()

    py.display.set_caption("Cubes")

    clock = py.time.Clock()

    reset()

def reset():
    logger.info("Reset")

    gamesurf.fill(colors["BLACK"])
    py.event.clear()

    cordOffset = 0, 0

    # Set standard equipment
    oldWeapon = weapons[0]
    oldArmor = armors[0]

    if len(characters) > 0:
        oldWeapon = characters.getPlayer().weapon
        oldArmor = characters.getPlayer().armor

    characters.empty()
    projectiles = []
    buildings = []

    pos = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
    tempCharacter = player(pos, 0, oldWeapon, oldArmor, baseSpeed, gamesurf)

    tempCharacter.addItem(items.getFromName("medKit"))

    for x in range(0, 5):
        tempCharacter.addItem(items.getFromName("bandage"))

    characters.append(tempCharacter)

    pos = (ra.randrange(0, WINDOWWIDTH), ra.randrange(0, WINDOWHEIGHT))
    team = 1
    buildings.append(nest(pos, team, gamesurf))

try:
    if __name__ == "__main__":
        main()

except:
    logger.critical(traceback.format_exc())

# Doing final cleanup
finally:
    py.quit()
    logger.info("Saving settings")
    with open("settings.json", "w") as f:
        json.dump(settings.getDict(), f, indent=4)
