import random
import pygame


class Pipe:
    WIDTH = 800
    HEIGHT = 600
    PIPE_WIDTH = 70
    PIPE_GAP = 150
    PIPE_SPEED = 3
    PIPE_SPAWN_TIME = 1.5

    def __init__(self, x):
        self.x = x
        self.height = random.randint(50, 400)
        self.passed = False

    def update(self):
        self.x -= self.PIPE_SPEED

    def draw(self, screen):
        # Top
        pygame.draw.rect(screen, (0, 200, 0),
                         (self.x, 0, self.PIPE_WIDTH, self.height))

        # Bottom
        pygame.draw.rect(screen, (0, 200, 0),
                         (self.x, self.height + self.PIPE_GAP,
                          self.PIPE_WIDTH, self.HEIGHT))

    def offscreen(self):
        return self.x + self.PIPE_WIDTH < 0
