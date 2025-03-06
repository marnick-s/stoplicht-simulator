import pygame
import os
import random
from lib.screen import screen, WIDTH, HEIGHT

class Car:
    def __init__(self, x, y, direction, speed=2, image_folder='assets/cars', sprite_width=44, sprite_height=24):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.turned = False
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        # Kies een willekeurige afbeelding uit de map (alleen WebP)
        self.image = self.load_random_image(image_folder)
        # Schaal de afbeelding naar de gewenste breedte en hoogte
        self.image = pygame.transform.scale(self.image, (sprite_width, sprite_height))
        
    def load_random_image(self, folder):
        # Verkrijg een lijst van alle WebP-afbeeldingsbestanden in de map
        image_files = [f for f in os.listdir(folder) if f.endswith('.webp')]
        if not image_files:
            raise ValueError("Geen WebP-afbeeldingen gevonden in de opgegeven map.")
        # Kies willekeurig een afbeelding
        image_file = random.choice(image_files)
        # Laad de gekozen afbeelding
        image_path = os.path.join(folder, image_file)
        return pygame.image.load(image_path)

    def move(self, obstacles):
        # Controleer eerst of de auto kan bewegen, d.w.z. of er geen botsing is
        if self.can_move(obstacles):
            if not self.turned:
                if self.direction == "right":
                    self.x += self.speed
                    if self.x > WIDTH // 2 - 30:
                        self.turned = True
                        self.direction = "up"
                elif self.direction == "left":
                    self.x -= self.speed
                    if self.x < WIDTH // 2 + 30:
                        self.turned = True
                        self.direction = "down"
                elif self.direction == "up":
                    self.y -= self.speed
                    if self.y < HEIGHT // 2 - 30:
                        self.turned = True
                        self.direction = "right"
                elif self.direction == "down":
                    self.y += self.speed
                    if self.y > HEIGHT // 2 + 30:
                        self.turned = True
                        self.direction = "left"
            else:
                if self.direction == "up":
                    self.y -= self.speed
                elif self.direction == "down":
                    self.y += self.speed
                elif self.direction == "right":
                    self.x += self.speed
                elif self.direction == "left":
                    self.x -= self.speed

    def can_move(self, obstacles):
        for car in obstacles:
            if car != self:
                # Controleer de overlap van de werkelijke grootte van de auto's
                if (self.x < car.x + car.sprite_width and
                    self.x + self.sprite_width > car.x and
                    self.y < car.y + car.sprite_height and
                    self.y + self.sprite_height > car.y):
                    return False  # Er is een botsing, dus de auto kan niet bewegen
        return True  # Geen botsing, de auto kan bewegen

    def draw(self):
        # Gebruik blit om de afbeelding op het scherm te tekenen
        screen.blit(self.image, (self.x, self.y))
