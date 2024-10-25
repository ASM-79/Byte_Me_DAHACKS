class Button():
    def __init__(self, image, pos, input, font, baseColor, hoverColor):
        self.image = image
        self.xPos = pos[0]
        self.yPos = pos[1]
        self.font = font
        self.baseColor, self.hoverColor = baseColor, hoverColor
        self.input = input
        self.text = self.font.render(self.input, True, self.baseColor) 

        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.xPos, self.yPos))
        self.text_rect = self.text.get_rect(center=(self.xPos, self.yPos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect) 

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
           return True
        return False
    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.input, True, self.hoverColor)
        else:
            self.text = self.font.render(self.input, True, self.baseColor)

