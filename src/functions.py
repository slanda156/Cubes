import pygame as py
from typing import Union


def scaleList(list: list, scale: int) -> list:
    """Multiply each element in the list by scale"""
    return [scale * i for i in list]


def positiveNum(num: Union[int, float]) -> int | float:
    """Returns the input when positiv or multiply by -1"""
    if num < 0:
        num += -1
    return num


def calcDist(pos1: Union[list[int, int], py.Vector2], pos2: Union[list[int, int], py.Vector2]) -> float:
    """Calculate the distance between both points using pygame.Vector2().lenght()"""
    distance = py.Vector2(pos2[0] - pos1[0], pos2[1] - pos1[1])
    return distance.length()


def findObjectInList(inList, var):
    if len(inList) <= 1:
        return 0
    else:
        for i in range(len(inList)-1):
            if inList[i].name == var:
                return i
