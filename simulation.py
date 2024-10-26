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
        # pygame.draw.circle(game.window, tuple(self.color), pos, self.scale)
        game.window.blit(self.image, (self.apos[0], self.apos[1]))
        self.render_v(game)

    def render_v(self, game):
        epos = (self.apos[0] + self.v[0] * METER, self.apos[1] - self.v[1] * METER)
        pygame.draw.line(game.window, (0, 0, 255), (self.apos[0], self.apos[1]), epos, 2)

    def render_a(self, game):
        epos = (self.apos[0] + self.a[0] * METER, self.apos[1] - self.a[1] * METER)
        pygame.draw.line(game.window, (255, 0, 0), (self.apos[0], self.apos[1]), epos, 2)

    def apply_physics(self, dt: float):
        # np.add(self.v, self.a * dt, out = self.v, casting='unsafe')
        # np.add(self.pos, self.v * dt, out = self.pos, casting='unsafe')
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
        # self.rocket = GameObject('planets.png/Rocket Option 1.png', 0.0, 0.4e5)
        # self.rocket.color[1] = 255
        # self.rocket.v[1] = -4.3e4
        # self.objects.append(self.rocket)
        # self.objects.append(GameObject('planets.png/moon1.png', 1.3e5, 0.0, 4.87e24))
        # self.objects.append(GameObject('planets.png/jupiter.png', -1.2e5, -1.3e5, 4.7e24))
        # self.objects[-1].v[1] = 2.3e4

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
        self.holded_callback = None
        # self.edit_obj = None
        for key, vals in main().items():
            self.objects.append(GameObject(key, vals[0].x, vals[0].y, vals[2], vals[3]))
            self.objects[-1].v[0] = np.array([vals[1].x, vals[1].y])
        # if planets == None:
        #     return
        # for key, vals in planets.items():
        #     pass

    def create_earth(self):
        self.objects.append(GameObject('planets.png/earth1.png', 0.0, 0.0, 5.97e24, 30))

    def earth_button_impl(self):
        self.holded_callback = self.create_earth

    def create_jupiter(self):
        self.objects.append(GameObject('planets.png/jupiter.png', 0.0, 0.0, 1.9e27, 40))

    def jupiter_button_impl(self):
        self.holded_callback = self.create_jupiter

    def create_mars(self):
        self.objects.append(GameObject('planets.png/mars1.png', 0.0, 0.0, 6.39e23, 22))

    def mars_button_impl(self):
        self.holded_callback = self.create_mars

    def create_sun(self):
        self.objects.append(GameObject('planets.png/Sun.png', 0.0, 0.0, 1.98e30, 80))

    def sun_button_impl(self):
        self.holded_callback = self.create_sun

    def create_mercury(self):
        self.objects.append(GameObject('planets.png/mercury1.png', 0.0, 0.0, 3.285e23, 20))

    def mercury_button_impl(self):
        self.holded_callback = self.create_mercury

    def create_venus(self):
        self.objects.append(GameObject('planets.png/venus1.png', 0.0, 0.0, 4.867e24, 28))

    def venus_button_impl(self):
        self.holded_callback = self.create_venus

    def create_rocket(self):
        self.objects.append(GameObject('planets.png/Rocket Option 1.png', 0.0, 0.0, 5e4))

    def rocket_button_impl(self):
        self.holded_callback = self.create_rocket

    def local_scene(self):
        data = get_scene('scenes/' + self.textBox.text + '.json')
        if data == None:
            return
        self.objects = []
        for key, vals in data.items():
            self.objects.append(GameObject(key, vals[0], vals[1], vals[-1]))
            self.objects[-1].v = np.array([vals[2], vals[3]])

    def start_button_impl(self):
        self.start_simulation = True
        # self.local_scene()

    def save_button_impl(self):
        if len(self.textBox.text) == 0:
            return
        data = {}
        for obj in self.objects:
            data[obj.image_path] = [obj.pos[0], obj.pos[1], obj.v[0], obj.v[1], obj.mass]
        save_scene('scenes/' + self.textBox.text + '.json', data)

    def render_ui(self):
        MenuMousePos = pygame.mouse.get_pos()

        for button in self.buttons:
            button.changeColor(MenuMousePos)
            button.update(self.window)

        self.textBox.render(self.window)

    def render(self):
        for obj in self.objects[::-1]:
            obj.render(self)

        self.render_ui()

    def collision(self):
        pass

    def update_simulations(self, dt):
        G = 6.67e-11
        for objA in self.objects:
            for objB in self.objects:
                if objB == objA:
                    continue
                d = np.linalg.norm(objA.pos - objB.pos)
                normal = (objA.pos - objB.pos) / d
                A = objA.mass * G / (d * d)
                objB.a += A * normal

        for obj in self.objects:
            obj.apply_physics(dt)

    def update(self, dt):
        if self.start_simulation:
            self.key_input()
            self.update_simulations(dt)

    def key_input(self):
        if self.textBox.focus:
            return
        speed = 10
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            SHIFT[0] += speed
        if keys[pygame.K_d]:
            SHIFT[0] -= speed
        if keys[pygame.K_w]:
            SHIFT[1] -= speed
        if keys[pygame.K_s]:
            SHIFT[1] += speed
        global METER
        if keys[pygame.K_j]:
            METER *= 0.99
        if keys[pygame.K_k]:
            METER *= 1 / 0.99

    def eventhandle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            MenuMousePos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.textBox.focus = self.textBox.textRect.collidepoint(event.pos)
                if event.button == 1 and self.holded_callback != None:
                    self.holded_callback()
                    self.mouse_pre = event.pos
                    self.objects[-1].pos[0] = (event.pos[0] - game.width / 2.0 - SHIFT[0]) / METER
                    self.objects[-1].pos[1] = (game.height / 2.0 - event.pos[1] - SHIFT[1]) / METER
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.holded_callback != None:
                    diff = [event.pos[0] - self.mouse_pre[0], self.mouse_pre[1] - event.pos[1]]
                    self.objects[-1].v[0] = diff[0] * 7000
                    self.objects[-1].v[1] = diff[1] * 7000
                    self.holded_callback = None
                for i in range(len(self.buttons)):
                    if self.buttons[i].checkForInput(MenuMousePos):
                        self.buttons_callback[i]()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.start_simulation = False
                    if len(self.textBox.text) == 0:
                        self.objects = []
                        return
                    self.local_scene()
                    return
                if event.key == pygame.K_SPACE:
                    self.start_simulation = not self.start_simulation
                self.textBox.update(event)
            elif event.type == pygame.VIDEORESIZE:
                self.width = event.w
                self.height = event.h

game = Game()
FPS = 60
time = pygame.time.Clock()
while game.running:
    game.eventhandle()
    game.window.fill(0x111111)
    game.render()
    game.update(1.0 / FPS)
    pygame.display.update()
    time.tick(FPS)

pygame.quit()
