import pygame
from lib.screen import screen, WIDTH, HEIGHT
from lib.vehicles.vehicle import Vehicle

class Boat(Vehicle):
    sprite_width = 44
    sprite_height = 24
    image_folder = "boats"

    def __init__(self, path, speed=2):
        super().__init__(path, speed, self.sprite_width, self.sprite_height, self.image_folder)