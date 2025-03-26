import pygame
import os
import random
from abc import ABC, abstractmethod
from lib.screen import screen

class Vehicle(ABC):
    def __init__(self, path, speed, sprite_width, sprite_height, image_folder):
        self.path = path
        self.current_target = 0
        self.x, self.y = self.path[self.current_target]
        self.speed = speed
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.image = self.scale_image(self.load_random_image("assets/vehicles/" + image_folder))

    def load_random_image(self, folder):
        image_files = [f for f in os.listdir(folder) if f.endswith('.webp')]
        if not image_files:
            raise ValueError(f"Geen WebP-afbeeldingen gevonden in de map: {folder}")
        image_file = random.choice(image_files)
        image_path = os.path.join(folder, image_file)
        return pygame.image.load(image_path)

    def scale_image(self, image):
        return pygame.transform.scale(image, (self.sprite_width, self.sprite_height))

    def move(self):
        if self.current_target < len(self.path) - 1:
            target_x, target_y = self.path[self.current_target + 1]
            dx, dy = target_x - self.x, target_y - self.y
            distance = max(1, (dx**2 + dy**2) ** 0.5)
            self.x += self.speed * dx / distance
            self.y += self.speed * dy / distance
            if abs(self.x - target_x) < self.speed and abs(self.y - target_y) < self.speed:
                self.current_target += 1

    def draw(self):
        screen.blit(self.image, (self.x, self.y))
