import pygame
import os
import random
from lib.collidable_object import CollidableObject, Hitbox
from lib.screen import screen, scale_to_display

class Vehicle(CollidableObject):
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
    
    def hitbox(self):
        return Hitbox(
            x=self.x,
            y=self.y,
            width=self.sprite_width,
            height=self.sprite_height,
        )

    def move(self, obstacles):
        if self.current_target < len(self.path) - 1:
            target_x, target_y = self.path[self.current_target + 1]
            dx, dy = target_x - self.x, target_y - self.y
            distance = max(1, (dx**2 + dy**2) ** 0.5)
            
            new_x = self.x + self.speed * dx / distance
            new_y = self.y + self.speed * dy / distance
            
            if self.can_move(obstacles):
                self.x = new_x
                self.y = new_y
                
                if abs(self.x - target_x) < self.speed and abs(self.y - target_y) < self.speed:
                    self.current_target += 1
                
    def is_occupying_sensor(self, directions):
        for direction in directions:
            for traffic_light in direction.traffic_lights:
                if (self.x <= traffic_light.front_sensor_position.x <= self.x + self.sprite_width and
                    self.y <= traffic_light.front_sensor_position.y <= self.y + self.sprite_height):
                    return direction, traffic_light, False
        return None, None, None
    
    def can_move(self, obstacles):
        for obstacle in obstacles:
            if obstacle != self and obstacle.can_collide():
                if self.hitbox().collides_with(obstacle.hitbox()):
                    return False
        return True
    
    def has_finished(self):
        return self.current_target >= len(self.path) - 1

    def draw(self):
        # pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.sprite_width, self.sprite_height), 2)

        scaled_x, scaled_y = scale_to_display(self.x, self.y)
        screen.blit(self.image, (scaled_x, scaled_y))
