import math
import pygame
import os
import random
from lib.collidable_object import CollidableObject, Hitbox
from lib.directions.traffic_light import TrafficLight
from lib.screen import screen, scale_to_display

class Vehicle(CollidableObject):
    def __init__(self, path, speed, sprite_width, sprite_height, image_folder):
        self.path = path
        self.current_target = 0
        self.x, self.y = self.path[self.current_target]
        self.speed = speed
        self.sprite_width, self.sprite_height = sprite_width, sprite_height
        self.original_image = self.scale_image(self.load_random_image("assets/vehicles/" + image_folder))
        self.angle = 0
        self.image = self.original_image.copy()
        self.rotated_width = self.sprite_width
        self.rotated_height = self.sprite_height


    def load_random_image(self, folder):
        image_files = [f for f in os.listdir(folder) if f.endswith('.webp')]
        if not image_files:
            raise ValueError(f"Geen WebP-afbeeldingen gevonden in de map: {folder}")
        image_file = random.choice(image_files)
        image_path = os.path.join(folder, image_file)
        return pygame.image.load(image_path)


    def scale_image(self, image):
        return pygame.transform.scale(image, (self.sprite_width, self.sprite_height))
    

    def hitboxes(self):
        num_segments = 4  # Meer = preciezere botsingen
        segment_length = (self.sprite_height + (self.sprite_height * 0.4)) // num_segments
        vehicle_width = self.sprite_width // 3  # breder dan voorheen

        hitboxes = []

        for i in range(num_segments):
            offset_distance = (i - num_segments / 2 + 0.5) * segment_length

            offset_x = math.cos(math.radians(self.angle)) * offset_distance
            offset_y = -math.sin(math.radians(self.angle)) * offset_distance

            hitbox = Hitbox(
                x=self.x + offset_x - vehicle_width // 2,
                y=self.y + offset_y - vehicle_width // 2,
                width=vehicle_width,
                height=vehicle_width
            )
            hitboxes.append(hitbox)

        return hitboxes


    def move(self, obstacles):
        if self.current_target < len(self.path) - 1:
            target_x, target_y = self.path[self.current_target + 1]
            dx, dy = target_x - self.x, target_y - self.y
            distance = max(1, (dx**2 + dy**2) ** 0.5)
            
            new_x = self.x + self.speed * dx / distance
            new_y = self.y + self.speed * dy / distance
            
            if self.can_move(obstacles, new_x, new_y):
                self.x = new_x
                self.y = new_y
                self.rotate_to_path()
                if abs(self.x - target_x) < self.speed and abs(self.y - target_y) < self.speed:
                    self.current_target += 1
                

    def is_occupying_sensor(self, directions):
        for direction in directions:
            for traffic_light in direction.traffic_lights:
                for hitbox in self.hitboxes():
                    if (hitbox.x <= traffic_light.front_sensor_position.x <= hitbox.x + hitbox.width and
                        hitbox.y <= traffic_light.front_sensor_position.y <= hitbox.y + hitbox.height):
                        return direction, traffic_light, False
        return None, None, None
    

    def can_move(self, obstacles, new_x, new_y):
        temp_x, temp_y = self.x, self.y
        self.x, self.y = new_x, new_y  # temporary position
        can_move = True
        for obstacle in obstacles:
            if self.collides_with(obstacle, only_front=True):
                can_move = False
                break
        self.x, self.y = temp_x, temp_y  # revert to original position
        return can_move

    

    def rotate_to_path(self):
        if self.current_target < len(self.path) - 1:
            # Get current and next path segment
            start_x, start_y = self.path[self.current_target]
            end_x, end_y = self.path[self.current_target + 1]
            
            # Calculate rotation angle using path direction
            dx = end_x - start_x
            dy = end_y - start_y
            self.angle = math.degrees(math.atan2(-dy, dx))  # Negative dy for pygame's coordinate system
            
            # Rotate image while maintaining original quality
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            
            # Store rotated dimensions for hitbox calculation
            self.rotated_width = self.image.get_width()
            self.rotated_height = self.image.get_height()


    def has_finished(self):
        return self.current_target >= len(self.path) - 1


    def draw(self):
        draw_x = self.x - self.rotated_width // 2
        draw_y = self.y - self.rotated_height // 2
        scaled_image = pygame.transform.scale(self.image, scale_to_display(self.rotated_width, self.rotated_height))
        screen.blit(scaled_image, scale_to_display(draw_x, draw_y))
        
        for hitbox in self.hitboxes():
            hitbox_x, hitbox_y = scale_to_display(hitbox.x, hitbox.y)
            hitbox_width, hitbox_height = scale_to_display(hitbox.width, hitbox.height)
            pygame.draw.rect(screen, (0, 255, 0), (hitbox_x, hitbox_y, hitbox_width, hitbox_height), 2)