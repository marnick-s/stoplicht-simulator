import pygame
from lib.screen import screen, scale_to_display

class Bridge():
    def __init__(self):
        self.position = (1388, 910)
        width, height = (107, 30)
        bridge_sprite = pygame.image.load('assets/brug-wegdek.webp').convert_alpha()
        self.bridge_sprite = pygame.transform.scale(bridge_sprite, scale_to_display(width, height))
        self.angle = 33

    def update(self):
        pass

    def draw(self):
        x, y = self.position
        rotated_sprite = pygame.transform.rotate(self.bridge_sprite, self.angle)
        rect = rotated_sprite.get_rect(center=scale_to_display(x, y))
        screen.blit(rotated_sprite, rect.topleft)
