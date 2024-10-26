import pygame, sys
from button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1920, 1080))
BG = pygame.image.load("images/spacebackground_1920x1080.png")
TRIMOON = pygame.image.load("images/tri2.png")
AASHEERMOON = pygame.image.load("images/aasheer5.png")
HARISHMOON = pygame.image.load("images/harish2.png")
JOEMOON = pygame.image.load("images/joe2.png")
SPACEMAN = pygame.image.load("images/spacedab2.png")


def get_font(size):
    return pygame.font.Font("images/TitleFont.ttf", size)


def play():
    while True:
        playMousePos = pygame.mouse.get_pos()
        SCREEN.fill("BLACK")

        playText = get_font(40).render("Placeholder", True, "White")
        playRect = playText.get_rect(center=(760,260))
        SCREEN.blit(playText, playRect)

        playBack = Button(image=None, pos=(760,460),
        input = "BACK", font=get_font(75),baseColor=("White"),hoverColor=("Yellow"))
        playBack.changeColor(playMousePos)
        playBack.update(SCREEN)


def main_menu():
    while True:
        SCREEN.blit(BG, (0,0))
        SCREEN.blit(SPACEMAN, (450, 250))
        SCREEN.blit(AASHEERMOON, (-110, 60))
        SCREEN.blit(TRIMOON, (-50, 600) )
        SCREEN.blit(JOEMOON, (1250, 60))
        SCREEN.blit(HARISHMOON, (1250, 550 ))
        MenuMousePos = pygame.mouse.get_pos()
        menuText = get_font(75).render("SPACE EXPLORERS", True, "#f2b333")
        menuRect = menuText.get_rect(center=(760, 100))

        playButton = Button(image=pygame.image.load("images/Play Rect.png"), pos=(750, 250), input="START", font=get_font(75), baseColor="White", hoverColor="#61f255")
        quitButton = Button(image=pygame.image.load("images/Quit Rect.png"), pos=(750, 650), input="EXIT", font=get_font(75), baseColor="White", hoverColor="#61f255")


        SCREEN.blit(menuText, menuRect)

        for button in (playButton, quitButton):
            button.changeColor(MenuMousePos)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if playButton.checkForInput(MenuMousePos):
                    play()
                if quitButton.checkForInput(MenuMousePos):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()
main_menu()









