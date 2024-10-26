import pygame
import numpy as np
from HUD import *
from HUD.button import *
import json
from instantpos import *

hardcode = {'Sun': [0, 0, 0.0, 0.0, 1.989e+30, 696340], 'mercury1': [1054424939.3301, -61299538896.77935, 39420.20912972592, 12495.454884449817, 3.3011e+23, 2439.7], 'venus1': [68398493435.107704, -76771820991.15689, 33913.7455697699, 12868.506551727365, 4.8675e+24, 6051.8], 'earth1': [121392171106.1312, 78675201368.78328, -17456.168464899947, 22366.22778518606, 5.97237e+24, 6371], 'mars1': [49925792525.30549, 204740417383.5171, -22713.50011224464, 6525.46094852942, 6.4171e+23, 3389.5], 'jupiter': [229264565681.17755, 665365767582.559, -12615.07585301929, 4101.341376243874, 1.8982e+27, 69911], 'saturn1': [1411977825282.14, -271282222896.31216, 865.4696030793367, 8891.707858123425, 5.6834e+26, 58232], 'uranus1': [1692594881843.4272, 2195866821687.7212, -5621.0076976069695, 3296.0637316781504, 8.681e+25, 25362], 'Neptune': [4471785354228.432, -75186220400.88289, 33.942090815791374, 5082.080306392246, 1.02413e+26, 24622]}

# METER = 0.0015
# METER = 0.000015
METER = 2.14e-10
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

class UiText:
    def __init__(self, window, text, font, pos, baseColor):
        text = font.render(text, True, baseColor)
        text_rect = text.get_rect(center=pos)
        window.blit(text, text_rect)

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
        self.simulation_time = 0

        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.window.fill(0x111111)
        self.background = pygame.image.load('planets.png/background_simu.jpg')

        self.objects = []

        self.textBox = UiTextBox(24, (10, 20, 140, 32), "#61f255")

        self.buttons = [
                Button(image=None, pos=(40, 80), input="START", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(40, 120), input="SAVE", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 180 - 60), input="SOLAR", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 220 - 60), input="EARTH", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 260 - 60), input="JUPITER", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 300 - 60), input="MARS", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 340 - 60), input="SUN", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 380 - 60), input="MERCURY", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 420 - 60), input="VENUS", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 460 - 60), input="SATURN", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 500 - 60), input="NEPTUNE", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 540 - 60), input="URANUS", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(self.width - 75, 580 - 60), input="ROCKET", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
        ]
        self.buttons_callback = [
                self.start_button_impl,
                self.save_button_impl,
                self.solar_button_impl,
                self.earth_button_impl,
                self.jupiter_button_impl,
                self.mars_button_impl,
                self.sun_button_impl,
                self.mercury_button_impl,
                self.venus_button_impl,
                self.saturn_button_impl,
                self.neptune_button_impl,
                self.uranus_button_impl,
                self.rocket_button_impl
        ]

        self.sliders = [
            Slider((840, 30), 100, 0.5, 10.0, 1.0),
        ]

        self.holded_callback = None

    def setup_solar_sys(self):
        # for key, vals in main().items():
        for key, vals in hardcode.items():
            self.objects.append(GameObject('planets.png/' + key + '.png', float(vals[0]), float(vals[1]), float(vals[4])))
            self.objects[-1].v[0] = float(vals[2])
            self.objects[-1].v[1] = float(vals[3])

    def solar_button_impl(self):
        self.setup_solar_sys()

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

    def create_saturn(self):
        self.objects.append(GameObject('planets.png/saturn1.png', 0.0, 0.0, 5.683e26, 38))

    def saturn_button_impl(self):
        self.holded_callback = self.create_saturn

    def create_neptune(self):
        self.objects.append(GameObject('planets.png/Neptune.png', 0.0, 0.0, 1.024e26, 20))

    def neptune_button_impl(self):
        self.holded_callback = self.create_neptune

    def create_uranus(self):
        self.objects.append(GameObject('planets.png/uranus1.png', 0.0, 0.0, 8.681e25, 25))

    def uranus_button_impl(self):
        self.holded_callback = self.create_uranus

    def create_rocket(self):
        self.objects.append(GameObject('planets.png/Rocket Option 1.png', 0.0, 0.0, 5e4))

    def rocket_button_impl(self):
        self.holded_callback = self.create_rocket

    def local_scene(self):
        # if self.textBox.text == '.solar':
        #     self.objects = []
        #     self.setup_solar_sys()
        #     self.simulation_time = 0
        #     return
        data = get_scene('scenes/' + self.textBox.text + '.json')
        if data == None:
            return
        self.objects = []
        for key, vals in data.items():
            self.objects.append(GameObject(key, vals[0], vals[1], vals[-1]))
            self.objects[-1].v = np.array([vals[2], vals[3]])
        self.simulation_time = 0

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

        UiText(self.window, 'zoom', pygame.font.Font(None, 24), (self.width - 150, 40), "#ffffff")
        for slider in self.sliders:
            slider.render(self.window)

        weeks = self.simulation_time / (3600 * 24 * 7)
        UiText(self.window, f'{weeks:.{2}f}' + 'w', pygame.font.Font(None, 24), (self.width // 2, 30), "#61f255")

        self.textBox.render(self.window)

    def render(self):
        self.window.blit(self.background, (0, 0))

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
            self.simulation_time += 1.98e4

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
            for slider in self.sliders:
                value = slider.handle_event(event)
                if value is not None:
                    global METER
                    METER = 2.14e-10 * (value)
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
                    self.objects[-1].v[0] = diff[0] * 1000
                    self.objects[-1].v[1] = diff[1] * 1000
                    self.holded_callback = None
                for i in range(len(self.buttons)):
                    if self.buttons[i].checkForInput(MenuMousePos):
                        self.buttons_callback[i]()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.start_simulation = False
                    if len(self.textBox.text) == 0:
                        self.objects = []
                        self.simulation_time = 0
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
# 1s -> 6k h(S)
while game.running:
    game.eventhandle()
    game.window.fill(0x111111)
    game.render()
    game.update(1.98e4)
    # game.update(1.0 / FPS)
    pygame.display.update()
    time.tick(FPS)

pygame.quit()
