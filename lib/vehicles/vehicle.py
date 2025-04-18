import math
import pygame
import os
import random
from lib.collidable_object import CollidableObject, Hitbox
from lib.screen import screen, scale_to_display
from lib.vehicles.supports_collision_free_zones import SupportsCollisionFreeZones

class Vehicle(CollidableObject):
    collision_free_zones = []

    def __init__(self, path, speed, sprite_width, sprite_height, vehicle_type_string):
        self.path = path
        self.current_target = 0
        self.x, self.y = self.path[self.current_target]
        self.speed = speed
        self.vehicle_type_string = vehicle_type_string
        self.sprite_width, self.sprite_height = sprite_width, sprite_height
        self.original_image = self.scale_image(self.load_random_image("assets/vehicles/" + self.vehicle_type_string))
        self.angle = 0
        self.image = self.original_image.copy()
        self.rotated_width = self.sprite_width
        self.rotated_height = self.sprite_height
        self._cached_hitboxes = None # Performance
        self._last_position = (self.x, self.y) # Performance
        self._last_angle = self.angle # Performance


    def load_random_image(self, folder):
        image_files = [f for f in os.listdir(folder) if f.endswith('.webp')]
        if not image_files:
            raise ValueError(f"Geen WebP-afbeeldingen gevonden in de map: {folder}")
        image_file = random.choice(image_files)
        image_path = os.path.join(folder, image_file)
        return pygame.image.load(image_path).convert_alpha()


    def scale_image(self, image):
        return pygame.transform.scale(image, scale_to_display(self.sprite_width, self.sprite_height))
    

    def hitboxes(self):
        # Cache hitboxes als positie en hoek niet veranderd zijn
        if self._cached_hitboxes is not None and (self.x, self.y) == self._last_position and self.angle == self._last_angle:
            return self._cached_hitboxes

        # Bereken hitboxes
        num_segments = 4
        segment_length = (self.sprite_height + (self.sprite_height * 0.4)) // num_segments
        vehicle_width = self.sprite_width // 3.4
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

        self._cached_hitboxes = hitboxes
        self._last_position = (self.x, self.y)
        self._last_angle = self.angle
        return hitboxes
    

    def move(self, obstacles):
        if isinstance(self, SupportsCollisionFreeZones) and self.exiting and not self.is_in_zone():
            self.exiting = False
    
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


    def can_move(self, obstacles, new_x, new_y):
        can_move = True
        
        if isinstance(self, SupportsCollisionFreeZones) and self.is_in_zone():
            if (self.exiting):
                return True
            current_zone = self.get_current_zone()
            if not self.point_in_zone(new_x, new_y, current_zone):
                if not self.exit_zone(obstacles, new_x, new_y):
                    can_move = False

        temp_x, temp_y = self.x, self.y
        self.x, self.y = new_x, new_y  # tijdelijke positie

        for obstacle in obstacles:
            if isinstance(self, SupportsCollisionFreeZones) and isinstance(obstacle, SupportsCollisionFreeZones):
                if self.in_same_cf_zone(obstacle):
                    continue
                if self.exiting and self.get_current_zone() == obstacle.get_current_zone():
                    continue
            if self.collides_with(obstacle, vehicle_direction=self.get_vehicle_direction(), collision_angle=self.angle):
                can_move = False
                break
            
        self.x, self.y = temp_x, temp_y  # herstel originele positie
        return can_move
        

    def get_vehicle_direction(self):
        if -45 <= self.angle <= 45:
            return 'west'
        elif 45 < self.angle <= 135:
            return 'south'
        elif -135 <= self.angle < -45:
            return 'north'
        else:
            return 'east'


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
        screen_x, screen_y = scale_to_display(self.x, self.y)
        draw_x = int(screen_x - self.rotated_width // 2)
        draw_y = int(screen_y - self.rotated_height // 2)
        screen.blit(self.image, (draw_x, draw_y))
        
        # for hitbox in self.hitboxes():
        #     hitbox_x, hitbox_y = scale_to_display(hitbox.x, hitbox.y)
        #     hitbox_width, hitbox_height = scale_to_display(hitbox.width, hitbox.height)
        #     pygame.draw.rect(screen, (0, 255, 0), (hitbox_x, hitbox_y, hitbox_width, hitbox_height), 2)