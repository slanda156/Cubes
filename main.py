import json
import traceback
import random as ra
import pygame as py

from src.logger import logger
from src.config import (
    settings,
    screen,
    gamesurf,
    WINDOWWIDTH,
    WINDOWHEIGHT,
    characters,
    baseSpeed,
    fonts,
    images
)
from src.definition import COLORS
from src.gui import iconAndText, textWidget, button
from src.character import player, checkHits
from src.buildings import nest
from src.equipment import weapons, armors, items

def main():
    if not py.get_init():
        py.init()

    global settings

    currentScreen = screen("main_menu")
    running = True
    cordOffset = [0, 0]

    py.display.set_caption("Cubes")

    clock = py.time.Clock()

    weaponIndex = 0
    armorIndex = 0
    waveCooldown = 0
    hudMode = 0
    tempSettings = settings.copy()

    # Create buttons
    # Define widgets size & position
    resetButtonSize = (150, 40)
    resetButtonPos = ((WINDOWWIDTH//2)-(resetButtonSize[0]//2), (WINDOWHEIGHT//2)-resetButtonSize[1]//2)

    menuButtonSize = (150, 40)
    menuButtonPos = ((WINDOWWIDTH//2)-(menuButtonSize[0]//2), (WINDOWHEIGHT//2)-menuButtonSize[1]//2+50)

    upPos1 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4)+130)
    downPos1 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4)+80)
    upPos2 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4)+50)
    downPos2 = ((WINDOWWIDTH/2)-100, (WINDOWHEIGHT/4))

    # Define widgets COLORS["LIGHTRED"]
    armorText = textWidget(fonts["buttonFont"], armors[0].color, ((WINDOWWIDTH/2)-70, (WINDOWHEIGHT/4)+15), gamesurf)
    weaponText = textWidget(fonts["buttonFont"], weapons[0].color, ((WINDOWWIDTH/2)-70, (WINDOWHEIGHT/4)+90), gamesurf)
    quitText = textWidget(fonts["buttonFont"], COLORS["BLACK"], ((WINDOWWIDTH/2)-35, (WINDOWHEIGHT/3)+150), gamesurf)
    optionsText = textWidget(fonts["buttonFont"], COLORS["BLACK"], ((WINDOWWIDTH/2)-55, (WINDOWHEIGHT/3)+100), gamesurf)
    titletext = textWidget(fonts["title2Font"], (220, 220, 220), (WINDOWWIDTH/2-90, 150), gamesurf)
    deadText = textWidget(fonts["titleFont"], COLORS["RED"], (WINDOWWIDTH/2-100, WINDOWHEIGHT*0.2), gamesurf)
    playText = textWidget(fonts["buttonFont"], COLORS["BLACK"], ((WINDOWWIDTH/2)-30, (WINDOWHEIGHT/3)+50), gamesurf)
    menuText = textWidget(fonts["buttonFont"], COLORS["BLACK"], (menuButtonPos[0]+(menuButtonSize[0]*0.1), menuButtonPos[1]), gamesurf)
    resetText = textWidget(fonts["buttonFont"], COLORS["BLACK"], (resetButtonPos[0]+(resetButtonSize[0]*0.22), resetButtonPos[1]), gamesurf)
    pauseText = textWidget(fonts["titleFont"], COLORS["WHITE"], (WINDOWWIDTH/2-100, WINDOWHEIGHT*0.2), gamesurf)
    fpsText = textWidget(fonts["buttonFont"], COLORS["GREEN"], ((WINDOWWIDTH/2), 20), gamesurf)
    levelText = textWidget(fonts["buttonFont"], COLORS["GREEN"], (20, 50), gamesurf)
    healthText = textWidget(fonts["buttonFont"], COLORS["LIGHTRED"], (20, 20), gamesurf)
    resourcesText = textWidget(fonts["buttonFont"], COLORS["GREEN"], ((WINDOWWIDTH-200), 20), gamesurf)
    waveCooldownText = textWidget(fonts["titleFont"], COLORS["GREEN"], (WINDOWWIDTH/2, 20), gamesurf)

    effectIconText = iconAndText(None, 5, fonts["effectFont"], COLORS["ERRCOLOR"], "None", (40, WINDOWHEIGHT-80), gamesurf)
    equippedItemIconText = iconAndText(None, 2, fonts["itemFont"], COLORS["GREEN"], "None", (WINDOWWIDTH-180, 80), gamesurf)

    upWeaponButtonRect = py.Rect(upPos1[0], upPos1[1], 20, 20)
    downWeaponButtonRect = py.Rect(downPos1[0], downPos1[1], 20, 20)
    upArmorButtonRect = py.Rect(upPos2[0], upPos2[1], 20, 20)
    downArmorButtonRect = py.Rect(downPos2[0], downPos2[1], 20, 20)
    quitButton = py.Rect((WINDOWWIDTH/2)-40, (WINDOWHEIGHT/3)+150, 80, 40)
    playRect = py.Rect((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+50, 180, 40)
    optionsRect = py.Rect((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+100, 180, 40)

    menuButton = py.Rect(menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1])
    resetButton = py.Rect(resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1])

    backButton = py.Rect(WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2, 180, 40)
    applyButton = py.Rect(WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2-50, 180, 40)

    downTriangle = [py.Vector2(0, 0), py.Vector2(20, 0), py.Vector2(10, 10)]
    upTriangle = [py.Vector2(0, 10), py.Vector2(20, 10), py.Vector2(10, 0)]

    reset()

    # Main loop
    while running:
        gamesurf.fill(COLORS["BLACK"])
        time = (clock.get_time() / 1000)
        playerChar = characters.getPlayer() #TODO Rework for MP

        # Calculate current difficulty
        difficulty = round(playerChar.kills/(1/playerChar.level), 3)

        # Main event loop
        for event in py.event.get():
            # Breaks loop when window closes
            if event.type == py.QUIT:
                running = False

            if currentScreen.get() == "main_menu":
                # Check for left clicks
                if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                    # Get mouse position
                    mousePos = py.mouse.get_pos()

                    # Start
                    if playRect.collidepoint(mousePos):
                        currentScreen.set("game_running")
                        reset()

                    # Go to options
                    if optionsRect.collidepoint(mousePos):
                        currentScreen.set("options")

                    # Next weapon
                    elif upWeaponButtonRect.collidepoint(mousePos):
                        weaponIndex += 1

                    # Last weapon
                    elif downWeaponButtonRect.collidepoint(mousePos):
                        weaponIndex -= 1

                    # Next armor
                    elif upArmorButtonRect.collidepoint(mousePos):
                        armorIndex += 1

                    # Last armor
                    elif downArmorButtonRect.collidepoint(mousePos):
                        armorIndex -= 1

                    # Quit game
                    elif quitButton.collidepoint(mousePos):
                        running = False

            elif currentScreen.get() == "options":
                # Check for left clicks
                if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                    # Get mouse position
                    mousePos = py.mouse.get_pos()

                    # Back button
                    if backButton.collidepoint(mousePos):
                        currentScreen.set("main_menu")

                    # Apply settings
                    elif applyButton.collidepoint(mousePos):
                        settings = tempSettings

                    # Resolution up
                    elif backButton.collidepoint(mousePos):
                        pass

                    # Resolution down
                    elif backButton.collidepoint(mousePos):
                        pass

            elif currentScreen.get() == "game_running":
                if event.type == py.MOUSEBUTTONDOWN:
                    # Cycle through items UP
                    if event.button == 4:
                        playerChar.changeItem(1)

                    # Cycle through items DOWN
                    elif event.button == 5:
                        playerChar.changeItem(-1)

                if event.type == py.KEYDOWN:
                    # Changing pause status
                    if event.key == py.K_ESCAPE:
                        currentScreen.set("game_paused")

                    # Skip wave cooldwon
                    elif event.key == py.K_t and waveCooldown != 0:
                        waveCooldown = 0
                        oldLevel = playerChar.level

                    # Placing Tower
                    elif event.key == py.K_f and playerChar.resources >= playerChar.towerCost:
                        playerChar.spawnTower(playerChar.pos, playerChar.team, playerChar.towerWeapon, playerChar.level, playerChar.towerAccuracy)

                    # Using equiped item
                    elif event.key == py.K_e and playerChar.equipItem is not None:
                        playerChar.useItem()

                    # Change hud mode
                    elif event.key == py.K_F1:
                        if hudMode == 1:
                            hudMode = 0
                        else:
                            hudMode = 1

            elif currentScreen.get() == "game_paused" or currentScreen.get() == "death_screen":

                # Check for button clicks
                if event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE and currentScreen.get() == "game_paused":
                        currentScreen.set("game_running")

                elif event.type == py.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if resetButton.collidepoint(py.mouse.get_pos()):
                            reset()
                            currentScreen.set("game_running")

                        elif menuButton.collidepoint(py.mouse.get_pos()):
                            currentScreen.set("main_menu")

            elif currentScreen.get() == "game_inventory":
                pass

        if currentScreen.get() == "main_menu":

            # Draw text & icons
            titletext.draw("Cubes")

            py.draw.polygon(gamesurf, COLORS["BLUE"], (downTriangle[0]+upPos1, downTriangle[1]+upPos1, downTriangle[2]+upPos1))
            py.draw.polygon(gamesurf, COLORS["BLUE"], (upTriangle[0]+downPos1, upTriangle[1]+downPos1, upTriangle[2]+downPos1))
            py.draw.polygon(gamesurf, COLORS["BLUE"], (downTriangle[0]+upPos2, downTriangle[1]+upPos2, downTriangle[2]+upPos2))
            py.draw.polygon(gamesurf, COLORS["BLUE"], (upTriangle[0]+downPos2, upTriangle[1]+downPos2, upTriangle[2]+downPos2))
            py.draw.rect(gamesurf, COLORS["RED"], ((WINDOWWIDTH/2)-40, (WINDOWHEIGHT/3)+150, 80, 40))
            py.draw.rect(gamesurf, COLORS["GREY"], ((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+50, 180, 40))
            py.draw.rect(gamesurf, COLORS["GREY"], ((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+100, 180, 40))

            playText.draw("PLAY")
            optionsText.draw("OPTIONS")
            quitText.draw("QUIT")

            # Handeling weapon & armor selection
            if weaponIndex < 0:
                weaponIndex = len(weapons)-1

            elif weaponIndex > (len(weapons)-1):
                weaponIndex = 0

            if armorIndex < 0:
                armorIndex = len(armors)-1

            elif armorIndex > (len(armors)-1):
                armorIndex = 0

            # Draw weapon & armor selection
            weaponText.color = weapons[weaponIndex].color
            armorText.color = armors[armorIndex].color

            weaponText.draw(weapons[weaponIndex].displayName)
            armorText.draw(armors[armorIndex].displayName)

            playerChar.weapon = weapons[weaponIndex]
            playerChar.armor = armors[armorIndex]

        elif currentScreen.get() == "options":
            backButton = button((WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2), (180, 40), gamesurf, currentScreen.set, "main_menu")
            py.draw.rect(gamesurf, COLORS["GREY"], (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2, 180, 40))
            py.draw.rect(gamesurf, COLORS["GREY"], (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2-50, 180, 40))

            backText = textWidget(fonts["buttonFont"], COLORS["BLACK"], (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2), gamesurf)
            applyText = textWidget(fonts["buttonFont"], COLORS["BLACK"], (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2-50), gamesurf)

            backText.draw("Back")
            applyText.draw("Apply")

        elif currentScreen.get() == "game_running":
            # Getting pressed mouse buttons
            mouse = py.mouse.get_pressed()

            # Handel player shooting
            if mouse[0] == 1 and not playerChar.effects.checkForName("shocked") and playerChar.cooldown <= 0:
                playerChar.shoot()

            # Getting pressed keys
            keys = py.key.get_pressed()

            # Handeling player movment
            if not playerChar.effects.checkForName("shocked"):
                if keys[py.K_w]:
                    if keys[py.K_LSHIFT] and playerChar.boost > 0:
                        playerChar.pos[1] -= playerChar.movementSpeed * 2 * time
                        playerChar.boost -= 10

                    else:
                        playerChar.pos[1] -= playerChar.movementSpeed * time
                        playerChar.boost += 10

                if keys[py.K_s]:
                    if keys[py.K_LSHIFT] and playerChar.boost > 0:
                        playerChar.pos[1] += playerChar.movementSpeed * 2 * time
                        playerChar.boost -= 10

                    else:
                        playerChar.pos[1] += playerChar.movementSpeed * time
                        playerChar.boost += 10

                if keys[py.K_d]:
                    if keys[py.K_LSHIFT] and playerChar.boost > 0:
                        playerChar.pos[0] += playerChar.movementSpeed * 2 * time
                        playerChar.boost -= 10

                    else:
                        playerChar.pos[playerChar] += playerChar.movementSpeed * time
                        playerChar.boost += 10

                if keys[py.K_a]:
                    if keys[py.K_LSHIFT] and playerChar.boost > 0:
                        playerChar.pos[0] -= playerChar.movementSpeed * 2 * time
                        playerChar.boost -= 10

                    else:
                        playerChar.pos[0] -= playerChar.movementSpeed * time
                        playerChar.boost += 10

            # Handels wave cooldown
            if oldLevel != playerChar.level:
                if (playerChar.level % 10) == 0 and waveCooldown <= 0:
                    waveCooldown = 30
                    oldLevel = playerChar.level

            # Delete all enemie characters
            if waveCooldown > 0:
                for x in characters:
                    if x.team != 0:
                        try:
                            del characters[characters.index(x)]
                        except IndexError:
                            logger.warning("Character not deletet")

                # Print remaining time
                waveCooldownText.draw(round(waveCooldown, 1))
                waveCooldown -= time

            # Check for dead characters and delets them
            for x in characters:
                checkHits(x.shots, characters, characters)
                for z in x.shots:
                    if z.range <= 0:
                        try:
                            del x.shots[x.shots.index(z)]
                        except IndexError:
                            logger.warning("Projectile not deletet")
                    z.draw(cordOffset)

                if x.health <= 0:
                    if x.team == 0:
                        reset() #TODO Add death screen

                    else:
                        try:
                            del characters[characters.index(x)]
                        except IndexError:
                            logger.warning("Character not deletet")

            # Draws all objects and handels object specific funktions
            for x in buildings:
                x.draw(cordOffset, waveCooldown, gamesurf, time, difficulty, characters)
                x.resize()

            for x in characters:
                x.draw(cordOffset, time, playerChar)
                for w in x.towers:
                    w.draw(cordOffset)
                    checkHits(w.shots, characters, characters)
                    for z in w.shots:
                        if x.range <= 0:
                            try:
                                del x.shots[x.shots.index(x)]
                            except IndexError:
                                logger.warning("Projectile not deletet")
                        z.draw(cordOffset)
                if x.controlled:
                    # Change cord offset to move window
                    if x.newPos[0] < 500:
                        cordOffset[0] -= (500 - x.newPos[0])
                    if x.newPos[0] > (WINDOWWIDTH - 500):
                        cordOffset[0] += (x.newPos[0] - (WINDOWWIDTH - 500))
                    if x.newPos[1] < 500:
                        cordOffset[1] -= (500 - x.newPos[1])
                    if x.newPos[1] > (WINDOWHEIGHT - 500):
                        cordOffset[1] += (x.newPos[1] - (WINDOWHEIGHT - 500))

            # Display the hud
            for x in buildings:
                x.healthBar()

            for x in characters:
                x.healthBar()

            # Health text and bar
            healthText.draw(f"{round(playerChar.health, 1)}/{round(playerChar.maxHealth, 1)}")

            # Level, resources & curent item
            levelText.draw(f"Level: {playerChar.level}")

            resourcesText.draw(f"Resources: {round(playerChar.resources, 1)}")

            if len(playerChar.inventory) > 0:
                tempItem = playerChar.equipItem
                equippedItemIconText.draw(f"{tempItem.displayName}: {tempItem.uses}")
            else:
                equippedItemIconText.draw("No items")

            for x in playerChar.effect:
                effectIconText.icon = images.get(x.type)
                # Refine string out effect type
                text = str(x.type)[:1].upper() + str(x.type)[1:]
                effectIconText.draw(text)

            # Debug infos
            if hudMode == 1:
                fpsText.draw(f"FPS: {int(clock.get_fps())}")

        elif currentScreen.get() == "game_paused" or currentScreen.get() == "death_screen":
            py.draw.rect(gamesurf, COLORS["GREY"], (resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1]))
            py.draw.rect(gamesurf, COLORS["GREY"], (menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1]))

            # Print current title
            if currentScreen.get() == "game_paused":
                pauseText.draw("Paused")
            else:
                deadText.draw("You are Dead")

            resetText.draw("Restart")

            menuText.draw("Main Menu")

        elif currentScreen.get() == "game_inventory":
            pass

        py.display.update()

        if settings.fps <= 0 or settings.fps >= 999:
            clock.tick(120)
            logger.warning(f"FPS over/under limit ({settings.fps})")
        else:
            clock.tick(settings.fps)

def reset():
    logger.info("Reset")

    global cordOffset
    global characters
    global projectiles
    global buildings

    gamesurf.fill(COLORS["BLACK"])
    py.event.clear()

    cordOffset = 0, 0

    # Set standard equipment
    oldWeapon = weapons[0]
    oldArmor = armors[0]

    if len(characters) > 0:
        oldWeapon = characters.getPlayer().weapon
        oldArmor = characters.getPlayer().armor

    characters.clear()
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


cordOffset = [0, 0]
projectiles = []
buildings = []

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
