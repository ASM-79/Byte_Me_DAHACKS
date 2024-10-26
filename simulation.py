import pygame
import numpy as np
import matplotlib.pyplot as plt

METER = 0.0005
SCALE = 1.0

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
        pos = (game.width / 2.0 + self.pos[0] * METER * SCALE, game.height / 2.0 - self.pos[1] * METER * SCALE)
        # pygame.draw.circle(game.window, tuple(self.color), pos, self.scale)
        game.window.blit(self.image, pos)

    def apply_physics(self, dt: float):
        # np.add(self.v, self.a * dt, out = self.v, casting='unsafe')
        # np.add(self.pos, self.v * dt, out = self.pos, casting='unsafe')
        self.v += self.a * dt
        self.pos += self.v * dt
        self.a = 0

class Game:
    def __init__(self):
        self.width = 640
        self.height = 520
        self.running = True
        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        self.window.fill(0x111111)

        self.rocket = GameObject('planets.png/Rocket Option 1.png', 0.0, 0.4e5)
        self.rocket.color[1] = 255
        self.rocket.v[1] = -2.0e5
        self.objects = []
        self.objects.append(self.rocket)
        self.objects.append(GameObject('planets.png/moon1.png', 1.3e5, 0.0, 4.87e24))
        # self.objects.append(GameObject('white_circle.png', -1.6e5, 0.0, 4.87e24))

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
        global SCALE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # up
                    SCALE += 0.2;
                elif event.button == 5: # down
                    SCALE -= 0.2;

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
