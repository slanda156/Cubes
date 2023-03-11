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

    screen = "main_menu"
    running = True
    cordOffset = [0, 0]

    py.display.set_caption("Cubes")

    clock = py.time.Clock()

    reset()

    # Main loop
    while running:
        gamesurf.fill(colors["BLACK"])
        time = (clock.get_time() / 1000)
        playerChar = characters.getPlayer()

        # Defines the maximum amount of enemies
        if characters[playerChar].level <= 10:
            maxChar = characters[playerChar].level
        else:
            maxChar = 10

        # Calculate current difficulty
        difficulty = characters[playerChar].level

        # Main event loop
        for event in py.event.get():
            # Breaks loop when window closes
            if event.type == py.QUIT:
                running = False

            if screen == "main_menu":
                # Check for left clicks
                if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                    # Get mouse position
                    mousePos = py.mouse.get_pos()

                    # Start
                    if playRect.collidepoint(mousePos):
                        screen = "game_running"
                        reset()

                    # Go to options
                    if optionsRect.collidepoint(mousePos):
                        screen = "options"

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

            elif screen == "options":
                # Check for left clicks
                if event.type == py.MOUSEBUTTONDOWN and event.button == 1:
                    # Get mouse position
                    mousePos = py.mouse.get_pos()

                    # Back button
                    if backButton.collidepoint(mousePos):
                        screen = "main_menu"

                    # Apply settings
                    elif applyButton.collidepoint(mousePos):
                        settings = tempSettings

                    # Resolution up
                    elif backButton.collidepoint(mousePos):
                        pass

                    # Resolution down
                    elif backButton.collidepoint(mousePos):
                        pass

            elif screen == "game_running":
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
                        screen = "game_paused"

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

                elif event.type == py.MOUSEBUTTONDOWN:
                    # Teleport to mouse position and sets effect
                    if event.button == 3 and playerChar.charge >= 100:
                        playerChar.pos[0] = py.mouse.get_pos()[0] - cordOffset[0]
                        playerChar.pos[1] = py.mouse.get_pos()[1] - cordOffset[1]

                        playerChar.effect.append(effect("shocked", 1.5, 0, (64, 56, 201)))
                        playerChar.effectDuration = 2.5

            elif screen == "game_paused" or screen == "death_screen":

                # Check for button clicks
                if event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE and screen == "game_paused":
                        screen = "game_running"

                elif event.type == py.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if resetButton.collidepoint(py.mouse.get_pos()):
                            reset()
                            screen = "game_running"

                        elif menuButton.collidepoint(py.mouse.get_pos()):
                            screen = "main_menu"

            elif screen == "game_inventory":
                pass

        if screen == "main_menu":

            # Draw text & icons
            titletext.draw("Cubes")

            py.draw.polygon(gamesurf, BLUE, (downTriangle[0]+upPos1, downTriangle[1]+upPos1, downTriangle[2]+upPos1))
            py.draw.polygon(gamesurf, BLUE, (upTriangle[0]+downPos1, upTriangle[1]+downPos1, upTriangle[2]+downPos1))
            py.draw.polygon(gamesurf, BLUE, (downTriangle[0]+upPos2, downTriangle[1]+upPos2, downTriangle[2]+upPos2))
            py.draw.polygon(gamesurf, BLUE, (upTriangle[0]+downPos2, upTriangle[1]+downPos2, upTriangle[2]+downPos2))
            py.draw.rect(gamesurf, RED, ((WINDOWWIDTH/2)-40, (WINDOWHEIGHT/3)+150, 80, 40))
            py.draw.rect(gamesurf, colors["GREY"], ((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+50, 180, 40))
            py.draw.rect(gamesurf, colors["GREY"], ((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+100, 180, 40))

            playText.draw("PLAY")
            optionsText.draw("OPTIONS")
            quitText.draw("QUIT")

            # Handeling weapon & armor selection
            if weaponIndex < 0:
                weaponIndex = weaponNum-1

            elif weaponIndex > (weaponNum-1):
                weaponIndex = 0

            if armorIndex < 0:
                armorIndex = armorNum-1

            elif armorIndex > (armorNum-1):
                armorIndex = 0

            # Draw weapon & armor selection
            weaponText.color = weapons[weaponIndex].color
            armorText.color = armors[armorIndex].color

            weaponText.draw(weapons[weaponIndex].displayName)
            armorText.draw(armors[armorIndex].displayName)

            playerChar.weapon = weapons[weaponIndex]
            playerChar.armor = armors[armorIndex]

        elif screen == "options":
            backButton = button((WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2), (180, 40), gamesurf, changeScreen, "main_menu")
            py.draw.rect(gamesurf, colors["GREY"], (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2, 180, 40))
            py.draw.rect(gamesurf, colors["GREY"], (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2-50, 180, 40))

            setting1.draw()
            setting2.draw()
            setting3.draw()
            setting4.draw()

            backText = textWidget(buttonFont, colors["BLACK"], (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2), gamesurf)
            applyText = textWidget(buttonFont, colors["BLACK"], (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2-50), gamesurf)

            backText.draw("Back")
            applyText.draw("Apply")

        elif screen == "game_running":
            # Getting pressed mouse buttons
            mouse = py.mouse.get_pressed()

            # Handel player shooting
            if mouse[0] == 1 and not checkList(playerChar.effect, "shocked") and playerChar.cooldown <= 0:
                playerChar.shoot()

            # Getting pressed keys
            keys = py.key.get_pressed()

            # Handeling player movment
            if not checkList(playerChar.effect, "shocked"):
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
                        playerChar.pos[char] += playerChar.movementSpeed * time
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
                        except:
                            logger.warning("Character not deletet")

                # Print remaining time
                waveCooldownText.draw(round(waveCooldown, 1))
                waveCooldown -= time

            # Check for dead characters and delets them
            for x in characters:
                checkHits(x.shots, characters, characters)
                for z in x.shots:
                    for y in barriers:
                        if checkRectangle(y, z):
                            try:
                                del x.shots[x.shots.index(z)]
                            except:
                                logger.warning("Projectile not deletet")
                    if z.range <= 0:
                        try:
                            del x.shots[x.shots.index(z)]
                        except:
                            logger.warning("Projectile not deletet")
                    z.draw(cordOffset)

                if x.health <= 0:
                    if x.team == 0:
                        dead = True
                        reset()

                    else:
                        try:
                            del characters[characters.index(x)]
                        except:
                            logger.warning("Character not deletet")

            # Draws all objects and handels object specific funktions
            for x in buildings:
                x.draw(cordOffset, waveCooldown, gamesurf, time, difficulty, characters)
                x.resize()

            for x in characters:
                x.draw(cordOffset, time, lights, playerChar)
                for w in x.towers:
                    w.draw(cordOffset)
                    checkHits(w.shots, characters, characters)
                    for z in w.shots:
                        for y in barriers:
                            if checkRectangle(y, z):
                                try:
                                    del x.shots[x.shots.index(z)]
                                except:
                                    logger.warning("Projectile not deletet")
                        if x.range <= 0:
                            try:
                                del x.shots[x.shots.index(x)]
                            except:
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
            for x in towers:
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

        elif screen == "game_paused" or screen == "death_screen":
            py.draw.rect(gamesurf, colors["GREY"], (resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1]))
            py.draw.rect(gamesurf, colors["GREY"], (menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1]))

            # Print current title
            if screen == "game_paused":
                pauseText.draw("Paused")
            else:
                deadText.draw("You are Dead")

            resetText.draw("Restart")

            menuText.draw("Main Menu")

        elif screen == "game_inventory":
            pass

        py.display.update()

        if setFPS <= 0 or setFPS >= 999:
            clock.tick(120)
            logger.warning(f"FPS over/under limit ({setFPS})")
        else:
            clock.tick(setFPS)

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
