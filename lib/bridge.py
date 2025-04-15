import pygame
from lib.screen import screen, scale_to_display

class Bridge():
    def __init__(self):
        bridge_sprite = pygame.image.load('assets/brug-wegdek.webp').convert_alpha()
        self.bridge_sprite = pygame.transform.scale(bridge_sprite, (30, 30))

    def update(self):
        pass

    def draw(self):
        screen.blit(self.bridge_sprite, (0, 0))
