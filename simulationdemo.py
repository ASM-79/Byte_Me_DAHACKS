import pygame
import numpy as np
from HUD import *
from HUD.button import *
import json
from instantpos import *

# METER = 0.0015
METER = 0.00001
SHIFT = [0.0, 0.0]

def save_scene(name, data):
    with open(name, 'w') as write:
        json.dump(data, write)

def get_scene(name):
    data = None
    try:
        with open(name, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File {name} not found")
    return data

def normalize(vec):
    d = vec[0] * vec[0] + vec[1] * vec[1]
    return np.array(vec / (d ** 0.5))

class UiTextBox:
    def __init__(self, font_size, rect, color):
        self.focus = False
        self.text = ''
        self.textRect = pygame.Rect(rect)
        self.color = color
        self.font_size = font_size
        
    def render(self, window):
        if self.focus:
            pygame.draw.rect(window, (255, 255, 255), self.textRect, 2)
        else:
            pygame.draw.rect(window, (200, 200, 200), self.textRect, 2)
        textCaption = pygame.font.Font(None, self.font_size).render(self.text, True, self.color)
        window.blit(textCaption, (self.textRect.x + 5, self.textRect.y + 5))

    def update(self, event):
        if self.focus == False or len(self.text) > 15:
            return
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return
        self.text += event.unicode

class Slider:
    def __init__(self, pos, length, min_val, max_val, start_val):
        self.rect = pygame.Rect(pos[0], pos[1], length, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.dragging = False
        self.slider_pos = pos[0] + int((start_val - min_val) / (max_val - min_val) * length)

    def render(self, window):
        pygame.draw.rect(window, (200, 200, 200), self.rect, 2)
        pygame.draw.line(window, (100, 100, 100), (self.rect.x, self.rect.centery), (self.rect.x + self.rect.width, self.rect.centery), 2)
        pygame.draw.circle(window, (255, 0, 0), (self.slider_pos, self.rect.centery), 8)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            if event.pos[0] >= self.rect.x and event.pos[0] <= self.rect.x + self.rect.width:
                self.slider_pos = event.pos[0]
                self.value = self.min_val + (self.slider_pos - self.rect.x) / self.rect.width * (self.max_val - self.min_val)
                return self.value
        return None

class GameObject:
    def __init__(self, image_path, x: float = 0.0, y: float = 0.0, mass: float = 1.0, scale = 40.0):
        self.pos = np.array([x, y])
        self.v = np.array([0.0, 0.0])
        self.a = np.array([0.0, 0.0])
        self.scale = scale
        self.mass = mass
        self.color = [255, 1, 1]
        self.image_path = image_path
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.scale, self.scale))
        self.apos = [0, 0]

    def render(self, game):
        self.apos = [game.width / 2.0 + self.pos[0] * METER + SHIFT[0], game.height / 2.0 - self.pos[1] * METER - SHIFT[1]]
        game.window.blit(self.image, (self.apos[0], self.apos[1]))
        self.render_v(game)

    def render_v(self, game):
        epos = (self.apos[0] + self.v[0] * METER, self.apos[1] - self.v[1] * METER)
        pygame.draw.line(game.window, (0, 0, 255), (self.apos[0], self.apos[1]), epos, 2)

    def render_a(self, game):
        epos = (self.apos[0] + self.a[0] * METER, self.apos[1] - self.a[1] * METER)
        pygame.draw.line(game.window, (255, 0, 0), (self.apos[0], self.apos[1]), epos, 2)

    def apply_physics(self, dt: float):
        self.render_a(game)
        self.v += self.a * dt
        self.pos += self.v * dt
        self.a[0] = 0.0
        self.a[1] = 0.0

class Game:
    def __init__(self):
        self.width = 960
        self.height = 640
        self.running = True
        self.start_simulation = False
        self.mouse_pre = [0, 0]

        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.window.fill(0x111111)

        self.objects = []
        self.textBox = UiTextBox(24, (10, 20, 140, 32), "#61f255")

        self.buttons = [
            Button(image=None, pos=(40, 80), input="START", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
            Button(image=None, pos=(40, 120), input="SAVE", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
            Button(image=None, pos=(40, 240), input="EARTH", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
            Button(image=None, pos=(40, 280), input="JUPITER", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
            Button(image=None, pos=(40, 320), input="MARS", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
            Button(image=None, pos=(40, 360), input="SUN", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
            Button(image=None, pos=(40, 400), input="MERCURY", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
            Button(image=None, pos=(40, 440), input="VENUS", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
            Button(image=None, pos=(40, 480), input="ROCKET", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
        ]
        self.buttons_callback = [
            self.start_button_impl,
            self.save_button_impl,
            self.earth_button_impl,
            self.jupiter_button_impl,
            self.mars_button_impl,
            self.sun_button_impl,
            self.mercury_button_impl,
            self.venus_button_impl,
            self.rocket_button_impl
        ]

        self.sliders = [
            Slider((100, 80), 100, 0.5, 2.0, 1.0),
            Slider((100, 120), 100, 0.5, 2.0, 1.0),
            Slider((100, 240), 100, 0.5, 2.0, 1.0),
            Slider((100, 280), 100, 0.5, 2.0, 1.0),
            Slider((100, 320), 100, 0.5, 2.0, 1.0),
            Slider((100, 360), 100, 0.5, 2.0, 1.0),
            Slider((100, 400), 100, 0.5, 2.0, 1.0),
            Slider((100, 440), 100, 0.5, 2.0, 1.0),
            Slider((100, 480), 100, 0.5, 2.0, 1.0)
        ]

        self.holded_callback = None

    def start_button_impl(self):
        self.start_simulation = True

    def save_button_impl(self):
        if len(self.textBox.text) == 0:
            return
        data = {}
        for obj in self.objects:
            data[obj.image_path] = [obj.pos[0], obj.pos[1], obj.v[0], obj.v[1], obj.mass]
        save_scene('scenes/' + self.textBox.text + '.json', data)

    def eventhandle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            MenuMousePos = pygame.mouse.get_pos()

            for slider in self.sliders:
                value = slider.handle_event(event)
                if value is not None:
                    global METER
                    METER = 0.00001 * (2 - value)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_simulation = not self.start_simulation
                self.textBox.update(event)

    def render_ui(self):
        MenuMousePos = pygame.mouse.get_pos()

        for button in self.buttons:
            button.changeColor(MenuMousePos)
            button.update(self.window)

        for slider in self.sliders:
            slider.render(self.window)

        self.textBox.render(self.window)

    def render(self):
        for obj in self.objects[::-1]:
            obj.render(self)

        self.render_ui()

game = Game()
FPS = 60
time = pygame.time.Clock()
while game.running:
    game.eventhandle()
    game.window.fill(0x111111)
    game.render()
    pygame.display.update()
    time.tick(FPS)

pygame.quit()
