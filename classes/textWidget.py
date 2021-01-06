class textWidget:
    def __init__(self, font, color, pos, gamesurf):
        self.font = font
        self.color = color
        self.pos = pos
        self.gamesurf = gamesurf

    def draw(self, text):
        widget = self.font.render(str(text), True, self.color)

        self.gamesurf.blit(widget, self.pos)