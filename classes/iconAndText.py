# Import needed modules
import pygame as py

class iconAndText:
    def __init__(self, sprit, scale, font, textColor, text, pos, gamesurf):
        self.gamesurf = gamesurf
        self.sprit = sprit
        self.scale = scale
        self.font = font
        self.textColor = textColor
        self.text = text
        self.pos = pos

    def draw(self, text=None):
        if text is not None:
            self.text = text

        widget = self.font.render(str(self.text), True, self.textColor)

        if self.sprit is not None:
            gamesurf.blit(self.sprit, self.pos)
        self.gamesurf.blit(widget, (self.pos[0]+50, self.pos[1]))