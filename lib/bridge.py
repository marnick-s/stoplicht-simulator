import pygame
from lib.screen import screen, scale_to_display

class Bridge():
    def __init__(self):
        self.position = (1388, 910)
        self.base_width, self.base_height = (107, 30)
        self.width, self.height = self.base_width, self.base_height
        self.bridge_sprite = pygame.image.load('assets/brug-wegdek.webp').convert_alpha()
        self.angle = 33
        self.open = False

    def update(self, open=True):
        if open:
            self.height = 10

    def draw(self):
        x, y = self.position
        transformed_sprite = pygame.transform.scale(self.bridge_sprite, scale_to_display(self.width, self.height))
        rotated_sprite = pygame.transform.rotate(transformed_sprite, self.angle)
        rect = rotated_sprite.get_rect(center=scale_to_display(x, y))
        screen.blit(rotated_sprite, rect.topleft)