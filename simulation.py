import pygame
import numpy as np
import matplotlib.pyplot as plt

METER = 0.002

def normalize(vec):
    d = vec[0] * vec[0] + vec[1] * vec[1]
    return np.array(vec / (d ** 0.5))

class GameObject:
    def __init__(self, image_path, x: float = 0.0, y: float = 0.0, mass: float = 1.0):
        self.pos = np.array([x, y])
        self.v = np.array([0.0, 0.0])
        self.a = np.array([0.0, 0.0])
        self.scale = 40
        self.mass = mass
        self.color = [255, 1, 1]
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.scale, self.scale))

    def render(self, game):
        pos = (game.width / 2.0 + self.pos[0] * METER, game.height / 2.0 - self.pos[1] * METER)
        # pygame.draw.circle(game.window, tuple(self.color), pos, self.scale)
        game.window.blit(self.image, pos)
        self.render_v(game)

    def render_v(self, game):
        pos = (game.width / 2.0 + self.pos[0] * METER, game.height / 2.0 - self.pos[1] * METER)
        epos = (game.width / 2.0 + (self.pos[0] + self.v[0] * 0.3) * METER, game.height / 2.0 - (self.pos[1] + self.v[1] * 0.3) * METER)
        pygame.draw.line(game.window, (0, 0, 255), pos, epos, 2)

    def render_a(self, game):
        pos = (game.width / 2.0 + self.pos[0] * METER, game.height / 2.0 - self.pos[1] * METER)
        epos = (game.width / 2.0 + (self.pos[0] + self.a[0] * 0.3) * METER, game.height / 2.0 - (self.pos[1] + self.a[1] * 0.3) * METER)
        pygame.draw.line(game.window, (255, 0, 0), pos, epos, 2)

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
        self.mouse_pre = [0, 0]

        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        self.window.fill(0x111111)

        self.rocket = GameObject('planets.png/Rocket Option 1.png', 0.0, 0.4e5)
        self.rocket.color[1] = 255
        self.rocket.v[1] = -4.3e4
        self.objects = []
        self.objects.append(self.rocket)
        self.objects.append(GameObject('planets.png/moon1.png', 1.3e5, 0.0, 4.87e24))
        self.objects.append(GameObject('planets.png/moon1.png', -1.2e5, -1.3e5, 4.7e24))
        self.objects[-1].v[1] = 2.3e4

    def render(self):
        for i in range(1, len(self.objects)):
            self.objects[i].render(self)
        self.rocket.render(self)

    def collision(self):
        pass

    def update(self, dt):
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

    def eventhandle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left
                    mx, my = pygame.mouse.get_pos()
                    self.rocket.pos[0] = (mx - game.width / 2.0) / METER
                    self.rocket.pos[1] = (game.height / 2.0 - my) / METER
                    self.rocket.v[0] = 0.0
                    self.rocket.v[1] = 0.0
                    self.rocket.a[0] = 0.0
                    self.rocket.a[1] = 0.0


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
