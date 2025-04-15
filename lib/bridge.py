import pygame
from lib.screen import screen, scale_to_display

class Bridge():
    def __init__(self):
        self.position = (1388, 869)
        self.base_width, self.base_height = (107, 30)
        self.width, self.height = self.base_width, self.base_height
        self.bridge_sprite = pygame.image.load('assets/brug-wegdek.webp').convert_alpha()
        self.angle = 32.5
        self.open = False
        self.seconds = 8

    def update(self):
        if (self.open and self.height != 0):
            self.height -= self.base_height / (self.seconds * 30)
        if (not self.open and self.height != self.base_height):
            self.height += self.base_height / (self.seconds * 30)

    def update_state(self, color):
        if color == "groen":
            self.open = True
        elif color == "rood":
            self.open = False

    def draw(self):
        offset_factor = (self.base_height - self.height) / 10
        x, y = self.position
        x = x - offset_factor
        y = y - offset_factor
        transformed_sprite = pygame.transform.scale(
            self.bridge_sprite, scale_to_display(self.width, self.height)
        )
        rotated_sprite = pygame.transform.rotate(transformed_sprite, self.angle)
        rect = rotated_sprite.get_rect()
        rect.midtop = scale_to_display(x, y)
        screen.blit(rotated_sprite, rect.topleft)
