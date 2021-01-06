# Import needed modules
import pygame as py
from classes.functions import scaleColor

class light:
    def __init__(self, pos, color, intensity, gamesurf, sprit=None):
        self.gamesurf = gamesurf
        self.pos = pos
        self.size = (64, 64)
        self.center = py.Vector2(pos[0]+self.size[0]/2, pos[1]+self.size[1]/2)
        self.color = color
        self.radius = intensity * 50
        self.intensity = intensity
        self.sprit = sprit

        if sprit is not None:
            # Rescale the image
            self.sprit = py.transform.scale(sprit, self.size)

    def draw(self, offset):
        newPos = self.pos - offset
        newPos = (int(newPos[0]), int(newPos[1]))

        newCenter = self.center - offset
        newCenter = (int(newCenter[0]), int(newCenter[1]))

        intensity = self.intensity * 10

        i = 10
        r = 0

        while i > 0:
            # Calc the radius
            r = int((intensity * i) / 2)

            # Create new color and scale it
            newColor = scaleColor(self.color, 1-i/10)

            # Draw circle with curent range and transparancy
            py.draw.circle(self.gamesurf, newColor, newPos, r)

            # Reduce number of circles
            i -= 0.1

        # Check and draw sprit
        if self.sprit is not None:
            self.gamesurf.blit(self.sprit, newCenter)

    def getBrightnes(self, distance):
        intensity = self.intensity * 10

        b = ((1-distance)*2)/intensity

        return b