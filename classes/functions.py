# Import modules
import logging
import random as ra
from classes.constants import *

# Define logger
logger = logging.getLogger(__name__)

def initFunctions(l):
    global logger
    logger = l

def findPlayerChar(characters):
    for x in characters:
        if x.controlled:
            return characters.index(x)

def checkCircle(circle, projectile, radius):
    if calcDist(circle.pos, projectile.start) <= radius:
        return True
    else:
        return False

def checkRectangle(rectangle, projectile):
    rect = py.Rect(rectangle.pos[0], rectangle.pos[1], rectangle.size[0], rectangle.size[1])

    if rect.collidepoint(projectile.start + projectile.offset):
        return True
    else:
        return False

def checkList(inList, var):
    for x in inList:
        if x.type == var:
            return True
        else:
            return False

def findObjectInList(inList, var):
    if len(inList) <= 1:
        return 0

    else:
        for i in range(len(inList)-1):
            if inList[i].name == var:
                return i

def checkHits(projectiles, objects, characters):
    for x in projectiles:
        for y in objects:
            if x.team != y.team:
                if y.type == "tower" and checkRectangle(py.Rect(y.pos[0], y.pos[1], y.size[0], y.size[1]), x):
                    y.getHit(x.weapon)
                elif y.type == "player" and checkCircle(y, x, y.radius):
                    y.getHit(x.weapon)
                    if y.health <= 0:
                        if x.team == 0:
                            i = findPlayerChar(objects)
                            characters[i].xp += (characters[i].level*20)
                            characters[i].resources += ((y.level/3)*20)

                    try:
                        del projectiles[projectiles.index(x)]
                    except:
                        logger.warning("Projectile not deletet")

def offsetTrajectory(start, splatter):
    start[0] = int(start[0])
    start[1] = int(start[1])

    return py.Vector2(ra.randint(start[0]-splatter, start[0]+splatter), ra.randint(start[1]-splatter, start[1]+splatter))

def scaleColor(color, scale):
    r = int(color[0] * scale)
    g = int(color[1] * scale)
    b = int(color[2] * scale)
    return (r, g, b)

def calcDist(pos1, pos2):
    distance = py.Vector2(pos2[0]-pos1[0], pos2[1]-pos1[1])

    return distance.length()

def positiveNum(number):
    if number < 0:
        number -= number*2

    return number

def sculpt(pos, texture, color1, color2, color3, scale): # TODO
    pass

def canSeeTarget(char, target):
    # Check for visibility
    if not target.visible > char.awareness:
        return False

    # Check distance
    if calcDist(char.pos, target.pos) > 1500:
        return False

    return True

def getNearestChar(start, characters):
    distance = []
    minDist = [0, 0]
    if len(characters) > 1:
        for x in characters:
            distance.append((calcDist(start.pos, x.pos), characters.index(x)))

        for y in distance:
            if minDist[0] == 0:
                minDist = y

            elif minDist[0] > y[0]:
                minDist = y

        return characters[minDist[1]]

def getNearestFriendlyChar(start, characters):
    distance = []
    minDist = None

    if len(characters) > 1:
        for x in characters:
            if start.team == x.team:
                distance.append((calcDist(start.pos, x.pos), characters.index(x)))

        for y in distance:
            if minDist is None:
                minDist = y

            elif minDist[0] > y[0]:
                minDist = y

        return characters[minDist[1]]

def getNearestEnemieChar(start, characters):
    distance = []
    minDist = [0, 0]

    if len(characters) > 1:
        for x in characters:
            if start.team != x.team:
                distance.append((calcDist(start.pos, x.pos), characters.index(x)))

        for y in distance:
            if minDist[0] <= 0:
                minDist = y

            elif minDist[0] > y[0]:
                minDist = y

        return characters[minDist[1]]

def getLights(pos, lights):
    value = []

    for x in lights:
        if calcDist(x.pos, pos) < x.radius:
            value.append(x)

    return value

def mindTransport(start, target, characters):
    if start is not None and target is not None:
        oldChar = target
        characters[characters.index(target)] = start
        characters[characters.index(start)] = oldChar

def generatePointsAroundDot(pos, minVar, maxVar):
    points = []
    power = ra.randrange(minVar, maxVar)

    while len(points) < power:
        distance = []
        minVal = 0

        a = ra.randrange(-10, 10)
        b = ra.randrange(-10, 10)
        c = ra.randrange(40, 400)
        offset = py.Vector2(a, b)

        if offset.length() != 0:
            offset.scale_to_length(c)

        if len(points) > 1:
            for x in points:
                if calcDist(x, pos+offset) > 100:
                    distance.append((calcDist(x, pos+offset)))

            for x in distance:
                if minVal != 0:
                    if minVal < x:
                        minVal = x

                else:
                    minVal = x

            if minVal > 50:
                points.append(pos+offset)

        else:
            points.append(pos+offset)

    return points