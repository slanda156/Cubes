# Import modules
import json
import time as ti
import traceback
import random as ra
import pygame as py

# Import classes
from classes.weapons import *
from classes.armor import *
from classes.item import *
from classes.upgrade import *

from classes.character import character
from classes.effect import effect
from classes.iconAndText import iconAndText
from classes.light import light
from classes.nest import nest
from classes.textWidget import textWidget
from classes.settingWidget import settingField
from classes.button import button

# Import constants
from classes.constants import *

# Import functions
from classes.functions import *

# Define the window
setFPS = 60
cordOffset = py.Vector2(0, 0)
WINDOWHEIGHT= 0
WINDOWWIDTH = 0
fullscreen = False

logger.info(f"Starting, version: {version}")

# Define Variables

running = True
levelText = None
movement = "none"

characters = []
towers = []
projectiles = []
barriers = []
dots = []
nests = []
lights = []
tempSettings = []

hudMode = 0
waveCooldown = 0
oldLevel = 0
maxChar = 0
time = 0
weaponIndex = 0
armorIndex = 0
difficulty = 0

# Define reset
def reset():
    logger.info("Reset")

    gamesurf.fill(BLACK)
    py.event.clear()

    global levelText
    global barriers
    global characters
    global nests
    global projectiles
    global baseSpeed
    global towers
    global cordOffset
    global lights
    global settings
    global tempSettings

    tempSettings = settings

    cordOffset[0] = 0
    cordOffset[1] = 0

    oldWeapon = weapons[0]
    oldArmor = armors[0]

    if len(characters) > 0:
        oldWeapon = characters[findPlayerChar(characters)].weapon
        oldArmor = characters[findPlayerChar(characters)].armor

    characters = []
    projectiles = []
    barriers = []
    nests = []
    towers = []
    lights = []

    pos = (0, 0)
    lights.append(light(pos, ORANGE, 10, images.get("lamp1.png")))

    pos = (WINDOWWIDTH/2, WINDOWHEIGHT/2)
    tempCharacter = character(pos, None, 0, oldWeapon, oldArmor, baseSpeed, towerBaseCost, gamesurf, True)

    tempCharacter.addItem(items.get("medKit"))
    tempCharacter.equipItem = tempCharacter.inventory[0]

    for x in range(0, 5):
        tempCharacter.addItem(items.get("bandage"))

    characters.append(tempCharacter)

    pos = (ra.randrange(0, WINDOWWIDTH), ra.randrange(0, WINDOWHEIGHT))
    team = 1
    nests.append(nest(pos, team, gamesurf))

# Init of settings
def initSettings():
    global settings
    global WINDOWWIDTH
    global WINDOWHEIGHT
    global fullscreen
    
    # Open settings
    with open("settings.json", "r+") as f:
        # Load settings
        settings = json.load(f)
        display = settings.get("display")

    # Define screen resolution
    WINDOWWIDTH = display.get("resolutionX")
    WINDOWHEIGHT = display.get("resolutionY")
    fullscreen = display.get("fullscreen")

# Initialsation

# Init pygame
if not py.get_init():
    py.init()

# Load settings
initSettings()

# Sets the display
# Check if in fullscreen mode
if fullscreen:
    window = py.display.Info()
    WINDOWWIDTH = window.current_w
    WINDOWHEIGHT = window.current_h
    gamesurf = py.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), py.FULLSCREEN)
    
else:
    gamesurf = py.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

py.display.set_caption(f"Cubes v.{version}")

# Define setting windows
setting1 = settingField((200, 200), (200, 500), gamesurf)
setting2 = settingField((500, 200), (200, 500), gamesurf)
setting3 = settingField((800, 200), (200, 500), gamesurf)
setting4 = settingField((1100, 200), (200, 500), gamesurf)

# Creates the main clock
clock = py.time.Clock()

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

# Define widgets
armorText = textWidget(buttonFont, armors[0].color, ((WINDOWWIDTH/2)-70, (WINDOWHEIGHT/4)+15), gamesurf)
weaponText = textWidget(buttonFont, weapons[0].color, ((WINDOWWIDTH/2)-70, (WINDOWHEIGHT/4)+90), gamesurf)
quitText = textWidget(buttonFont, BLACK, ((WINDOWWIDTH/2)-35, (WINDOWHEIGHT/3)+150), gamesurf)
optionsText = textWidget(buttonFont, BLACK, ((WINDOWWIDTH/2)-55, (WINDOWHEIGHT/3)+100), gamesurf)
titletext = textWidget(title2Font, (220, 220, 220), (WINDOWWIDTH/2-90, 150), gamesurf)
deadText = textWidget(titleFont, RED, (WINDOWWIDTH/2-100, WINDOWHEIGHT*0.2), gamesurf)
playText = textWidget(buttonFont, BLACK, ((WINDOWWIDTH/2)-30, (WINDOWHEIGHT/3)+50), gamesurf)
menuText = textWidget(buttonFont, BLACK, (menuButtonPos[0]+(menuButtonSize[0]*0.1), menuButtonPos[1]), gamesurf)
resetText = textWidget(buttonFont, BLACK, (resetButtonPos[0]+(resetButtonSize[0]*0.22), resetButtonPos[1]), gamesurf)
pauseText = textWidget(titleFont, WHITE, (WINDOWWIDTH/2-100, WINDOWHEIGHT*0.2), gamesurf)
fpsText = textWidget(buttonFont, GREEN, ((WINDOWWIDTH/2), 20), gamesurf)
xpText = textWidget(buttonFont, GREEN, (20, 80), gamesurf)
levelText = textWidget(buttonFont, GREEN, (20, 50), gamesurf)
healthText = textWidget(buttonFont, LIGHTRED, (20, 20), gamesurf)
resourcesText = textWidget(buttonFont, GREEN, ((WINDOWWIDTH-200), 20), gamesurf)
waveCooldownText = textWidget(titleFont, GREEN, (WINDOWWIDTH/2, 20), gamesurf)

effectIconText = iconAndText(None, 5, effectFont, ERROCOLOR, "None", (40, WINDOWHEIGHT-80), gamesurf)
equippedItemIconText = iconAndText(None, 2, itemFont, GREEN, "None", (WINDOWWIDTH-180, 80), gamesurf)

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

# Resets all variables
reset()

logger.info(f"Loaded after: {round(ti.time()-startTime, 3)} s")

try:
    while running:
        # Resets backround
        gamesurf.fill(BLACK)
        # Sets global time variable
        time = (clock.get_time() / 1000)
        # Sets log time
        t = ti.localtime()
        currentTime = ti.strftime("%H_%M_%S", t)
        # Gets player charakter
        char = findPlayerChar(characters)

        # Defines the maximum amount of enemies
        if characters[char].level <= 10:
            maxChar = characters[char].level
        else:
            maxChar = 10

        # Calculate current difficulty
        difficulty = characters[char].level

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
                        characters[char].changeItem(1)

                    # Cycle through items DOWN
                    elif event.button == 5:
                        characters[char].changeItem(-1)

                if event.type == py.KEYDOWN:
                    # Changing pause status
                    if event.key == py.K_ESCAPE:
                        screen = "game_paused"

                    # Skip wave cooldwon
                    elif event.key == py.K_t and waveCooldown != 0:
                        waveCooldown = 0
                        oldLevel = characters[char].level

                    # Placing Tower
                    elif event.key == py.K_f and characters[char].resources >= characters[char].towerCost:
                        characters[char].spawnTower(characters[char].pos, characters[char].team, characters[char].towerWeapon, characters[char].level, characters[char].towerAccuracy)

                    # Using equiped item
                    elif event.key == py.K_e and characters[char].equipItem is not None:
                        characters[char].useItem()

                    # Change hud mode
                    elif event.key == py.K_F1:
                        if hudMode == 1:
                            hudMode = 0
                        else:
                            hudMode = 1

                elif event.type == py.MOUSEBUTTONDOWN:
                    # Teleport to mouse position and sets effect
                    if event.button == 3 and characters[char].charge >= 100:
                        characters[char].pos[0] = py.mouse.get_pos()[0] - cordOffset[0]
                        characters[char].pos[1] = py.mouse.get_pos()[1] - cordOffset[1]

                        characters[char].effect.append(effect("shocked", 1.5, 0, (64, 56, 201)))
                        characters[char].effectDuration = 2.5

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
            py.draw.rect(gamesurf, GREY, ((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+50, 180, 40))
            py.draw.rect(gamesurf, GREY, ((WINDOWWIDTH/2)-90, (WINDOWHEIGHT/3)+100, 180, 40))

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

            characters[char].weapon = weapons[weaponIndex]
            characters[char].armor = armors[armorIndex]

        elif screen == "options":
            backButton = button((WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2), (180, 40), gamesurf, changeScreen, "main_menu")
            py.draw.rect(gamesurf, GREY, (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2, 180, 40))
            py.draw.rect(gamesurf, GREY, (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2-50, 180, 40))

            setting1.draw()
            setting2.draw()
            setting3.draw()
            setting4.draw()

            backText = textWidget(buttonFont, BLACK, (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2), gamesurf)
            applyText = textWidget(buttonFont, BLACK, (WINDOWWIDTH/2-55, WINDOWHEIGHT/3*2-50), gamesurf)

            backText.draw("Back")
            applyText.draw("Apply")

        elif screen == "game_running":
            # Getting pressed mouse buttons
            mouse = py.mouse.get_pressed()

            # Handel player shooting
            if mouse[0] == 1 and not checkList(characters[char].effect, "shocked") and characters[char].cooldown <= 0:
                characters[char].shoot()

            # Getting pressed keys
            keys = py.key.get_pressed()

            # Handeling player movment
            if not checkList(characters[char].effect, "shocked"):
                if keys[py.K_w]:
                    if keys[py.K_LSHIFT] and characters[char].boost > 0:
                        characters[char].pos[1] -= characters[char].movementSpeed * 2 * time
                        characters[char].boost -= 10

                    else:
                        characters[char].pos[1] -= characters[char].movementSpeed * time
                        characters[char].boost += 10

                if keys[py.K_s]:
                    if keys[py.K_LSHIFT] and characters[char].boost > 0:
                        characters[char].pos[1] += characters[char].movementSpeed * 2 * time
                        characters[char].boost -= 10

                    else:
                        characters[char].pos[1] += characters[char].movementSpeed * time
                        characters[char].boost += 10

                if keys[py.K_d]:
                    if keys[py.K_LSHIFT] and characters[char].boost > 0:
                        characters[char].pos[0] += characters[char].movementSpeed * 2 * time
                        characters[char].boost -= 10

                    else:
                        characters[char].pos[char] += characters[char].movementSpeed * time
                        characters[char].boost += 10

                if keys[py.K_a]:
                    if keys[py.K_LSHIFT] and characters[char].boost > 0:
                        characters[char].pos[0] -= characters[char].movementSpeed * 2 * time
                        characters[char].boost -= 10

                    else:
                        characters[char].pos[0] -= characters[char].movementSpeed * time
                        characters[char].boost += 10

            # Handels wave cooldown
            if oldLevel != characters[char].level:
                if (characters[char].level % 10) == 0 and waveCooldown <= 0:
                    waveCooldown = 30
                    oldLevel = characters[char].level

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
            for x in lights:
                x.draw(cordOffset)

            for x in nests:
                x.draw(cordOffset, waveCooldown, gamesurf, time, difficulty, characters)
                x.resize()

            for x in barriers:
                x.draw(cordOffset)

            for x in characters:
                x.draw(cordOffset, time, lights, characters[char])
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
            healthText.draw(f"{round(characters[char].health, 1)}/{round(characters[char].maxHealth, 1)}")

            # Level, resources & curent item
            levelText.draw(f"Level: {characters[char].level}")

            resourcesText.draw(f"Resources: {round(characters[char].resources, 1)}")

            if len(characters[char].inventory) > 0:
                tempItem = characters[char].equipItem
                equippedItemIconText.draw(f"{tempItem.displayName}: {tempItem.uses}")
            else:
                equippedItemIconText.draw("No items")

            for x in characters[char].effect:
                effectIconText.icon = images.get(x.type)
                # Refine string out effect type
                text = str(x.type)[:1].upper() + str(x.type)[1:]
                effectIconText.draw(text)

            # Debug infos
            if hudMode == 1:
                fpsText.draw(f"FPS: {int(clock.get_fps())}")

        elif screen == "game_paused" or screen == "death_screen":
            py.draw.rect(gamesurf, GREY, (resetButtonPos[0], resetButtonPos[1], resetButtonSize[0], resetButtonSize[1]))
            py.draw.rect(gamesurf, GREY, (menuButtonPos[0], menuButtonPos[1], menuButtonSize[0], menuButtonSize[1]))

            # Print current title
            if screen == "game_paused":
                pauseText.draw("Paused")
            else:
                deadText.draw("You are Dead")

            resetText.draw("Restart")

            menuText.draw("Main Menu")

        elif screen == "game_inventory":
            pass

        # Updating the display
        py.display.update()

        # Tick the main clock with given fps
        if setFPS <= 0 or setFPS >= 120:
            clock.tick(120)
        else:
            clock.tick(setFPS)

# Catch any error an add it to the crash log
except:
    logging.critical(traceback.format_exc())

# Doing final cleanup
finally:
    # Stops all pygame modules and closes all windows
    py.quit()
    # Save settings to json
    logger.info("Saving settings")
    with open("settings.json", "w+") as f:
        json.dump(settings, f)
    # Prints end of log
    logger.info(f"Stopping after: {round(ti.time()-startTime, 3)} s")