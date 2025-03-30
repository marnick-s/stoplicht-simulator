import pygame
from lib.screen import screen, WIDTH, HEIGHT
from lib.vehicles.vehicle import Vehicle

class Boat(Vehicle):
    sprite_width = 44
    sprite_height = 24
    image_folder = "boats"
    speed = 2

    def __init__(self, path):
        super().__init__(path, self.speed, self.sprite_width, self.sprite_height, self.image_folder)