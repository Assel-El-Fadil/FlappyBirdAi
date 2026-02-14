import pygame

HEIGHT = 600
GRAVITY = 800
JUMP_FORCE = -300


class Bird:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.velocity = 0
        self.dead = False
        self.score = 0

    def jump(self):
        if not self.dead:
            self.velocity = JUMP_FORCE

    def update(self, dt):
        if not self.dead:
            self.velocity += GRAVITY * dt
            self.y += self.velocity * dt

            # Check boundaries
            if self.y - self.radius < 0 or self.y + self.radius > HEIGHT:
                self.dead = True

    def draw(self, screen):
        if not self.dead:
            circle_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA).convert_alpha()
            pygame.draw.circle(circle_surface, (255, 250, 250, 100),
                               (self.radius, self.radius), self.radius)
            screen.blit(circle_surface, (int(self.x) - self.radius, int(self.y) - self.radius))
