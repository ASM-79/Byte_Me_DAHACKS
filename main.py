import pygame, sys
from HUD.button import Button
from simulation import *

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
BG = pygame.image.load("HUD/images/spacebackground_1920x1080.png")
TRIMOON = pygame.image.load("HUD/images/tri2.png")
AASHEERMOON = pygame.image.load("HUD/images/aasheer5.png")
HARISHMOON = pygame.image.load("HUD/images/harish2.png")
JOEMOON = pygame.image.load("HUD/images/joe2.png")
SPACEMAN = pygame.image.load("HUD/images/spacedab2.png")

VolumeStd = 0.5

pygame.mixer.music.load("HUD/bgmusic.mp3")
pygame.mixer.music.set_volume(VolumeStd)
pygame.mixer.music.play(-1)


def get_font(size):
    return pygame.font.Font("HUD/images/TitleFont.ttf", size)


def play():
    simulationStart(True)
    # while True:
    #     testString = "Testing"
    #     playMousePos = pygame.mouse.get_pos()
    #     SCREEN.fill("black")

    #     playText = get_font(40).render(testString, True, "White")
    #     playRect = playText.get_rect(center=(760,260))
    #     SCREEN.blit(playText, playRect)

    #     playBack = Button(image=None, pos=(760,460),
    #     input = "BACK", font=get_font(75),baseColor=("White"),hoverColor=("Yellow"))
    #     playBack.changeColor(playMousePos)
    #     playBack.update(SCREEN)

    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             pygame.quit()
    #             sys.exit()
    #         if event.type == pygame.MOUSEBUTTONDOWN:
    #             if playBack.checkForInput(playMousePos):
    #                 main_menu()
    #     pygame.display.update()

def sound():
    global VolumeStd
    while True:
        soundMousePos = pygame.mouse.get_pos()
        
        soundText = get_font(40).render(f"Volume: {int(VolumeStd * 100)}%", True, "White")
        soundRect = soundText.get_rect(center=(960, 260))
        SCREEN.fill("black")
        SCREEN.blit(soundText, soundRect)

        soundUp = Button(image=None, pos=(960, 360), input="+", font=get_font(50), baseColor="White", hoverColor="Green")
        soundDown = Button(image=None, pos=(960, 460), input="-", font=get_font(50), baseColor="White", hoverColor="Red")
        soundBack = Button(image=None, pos=(960, 560), input="Back", font=get_font(50), baseColor="White", hoverColor="Yellow")

        for button in [soundUp, soundDown, soundBack]:
            button.changeColor(soundMousePos)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if soundUp.checkForInput(soundMousePos):
                    VolumeStd = min(1.0, VolumeStd + 0.1)  # Ensure volume doesn't exceed 1.0
                    pygame.mixer.music.set_volume(VolumeStd)
                if soundDown.checkForInput(soundMousePos):
                    VolumeStd = max(0.0, VolumeStd - 0.1)  # Ensure volume doesn't go below 0.0
                    pygame.mixer.music.set_volume(VolumeStd)
                if soundBack.checkForInput(soundMousePos):
                    main_menu()
                    return

        pygame.display.update()


def main_menu():
    while True:
        SCREEN.blit(BG, (0,0))
        SCREEN.blit(AASHEERMOON, (-110, 60))
        SCREEN.blit(TRIMOON, (-50, 600) )
        SCREEN.blit(JOEMOON, (1200, 60))
        SCREEN.blit(HARISHMOON, (1200, 550 ))
        MenuMousePos = pygame.mouse.get_pos()
        menuText = get_font(75).render("SPACE EXPLORERS", True, "#f2b333")
        menuRect = menuText.get_rect(center=(760, 100))

        playButton = Button(image=pygame.image.load("HUD/images/Play Rect.png"), pos=(750, 250), input="START", font=get_font(75), baseColor="White", hoverColor="#61f255")
        quitButton = Button(image=pygame.image.load("HUD/images/Quit Rect.png"), pos=(750, 650), input="EXIT", font=get_font(75), baseColor="White", hoverColor="#61f255")
        soundButton = Button(image=pygame.image.load("HUD/images/Sound Rect.png"), pos=(750,450), input="SOUND", font=get_font(75), baseColor="White", hoverColor="#61f255")

        SCREEN.blit(menuText, menuRect)

        for button in (playButton, quitButton, soundButton):
            button.changeColor(MenuMousePos)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if playButton.checkForInput(MenuMousePos):
                    play()
                if soundButton.checkForInput(MenuMousePos):
                    sound()
                if quitButton.checkForInput(MenuMousePos):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()


main_menu()









