import math
import pygame
import os
import random
import time
import re
from lib.collidable_object import CollidableObject, Hitbox
from lib.screen import screen, scale_to_display
from lib.vehicles.supports_collision_free_zones import SupportsCollisionFreeZones

class Vehicle(CollidableObject):
    collision_free_zones = []
    # For time-based movement
    last_update_time = time.time()

    def __init__(self, id, path, speed, vehicle_type_string):
        self.path = path
        self.id = id
        self.current_target = 0
        self.x, self.y = self.path[self.current_target]
        self.speed = speed  # Now in units per second
        self.vehicle_type_string = vehicle_type_string
        
        # Load image first to get dimensions from filename
        self.original_image, self.sprite_width, self.sprite_height = self.load_random_image_with_dimensions("assets/vehicles/" + self.vehicle_type_string)
        
        self.angle = 0
        self.image = self.original_image.copy()
        self.rotated_width = self.sprite_width
        self.rotated_height = self.sprite_height
        self._cached_hitboxes = None # Performance
        self._last_position = (self.x, self.y) # Performance
        self._last_angle = self.angle # Performance
        self.last_move_time = time.time()  # For time-based movement

    def after_create(self):
        pass
    
    def load_random_image_with_dimensions(self, folder):
        image_files = [f for f in os.listdir(folder) if f.endswith('.webp')]
        if not image_files:
            raise ValueError(f"Geen WebP-afbeeldingen gevonden in de map: {folder}")
        
        image_file = random.choice(image_files)
        
        # Extract dimensions from filename (e.g., "20x20.webp" or "20x20-1.webp")
        dimensions_match = re.search(r'(\d+)x(\d+)(?:-\d+)?\.webp$', image_file)
        if dimensions_match:
            sprite_width = int(dimensions_match.group(1))
            sprite_height = int(dimensions_match.group(2))
        else:
            # Default dimensions if pattern doesn't match
            sprite_width = 40
            sprite_height = 40
        
        image_path = os.path.join(folder, image_file)
        image = pygame.image.load(image_path).convert_alpha()
        scaled_image = self.scale_image(image, sprite_width, sprite_height)
        
        return scaled_image, sprite_width, sprite_height

    def scale_image(self, image, width, height):
        return pygame.transform.scale(image, scale_to_display(width, height))
    
    def hitboxes(self):
        # Cache hitboxes
        if self._cached_hitboxes is not None and (self.x, self.y) == self._last_position and self.angle == self._last_angle:
            return self._cached_hitboxes

        # Calculate hitboxes
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
    
    def calculate_next_position(self, obstacles):
        # Return current position if we have no more targets
        if self.current_target >= len(self.path) - 1:
            return {
                'x': self.x,
                'y': self.y,
                'speed': self.speed,
                'angle': self.angle,
                'current_target': self.current_target,
                'moved': False  # Flag to indicate if the vehicle actually moved
            }
        
        # Calculate elapsed time since last update for time-based movement
        current_time = time.time()
        elapsed_time = current_time - self.last_move_time
        
        # Get target position
        target_x, target_y = self.path[self.current_target + 1]
        dx, dy = target_x - self.x, target_y - self.y
        distance = max(1, (dx**2 + dy**2) ** 0.5)
        
        # Calculate time-based movement distance
        move_distance = self.speed * elapsed_time
        if move_distance > distance:
            move_distance = distance
        
        # Calculate new position
        new_x = self.x + move_distance * dx / distance
        new_y = self.y + move_distance * dy / distance
        
        # Calculate new angle
        new_angle = math.degrees(math.atan2(-dy, dx))
        
        # Check if can reach next target
        reached_target = False
        new_target = self.current_target
        if abs(new_x - target_x) < move_distance * 0.5 and abs(new_y - target_y) < move_distance * 0.5:
            new_target += 1
            reached_target = True
        
        # Check if the move is valid
        can_move = self.can_move(obstacles, new_x, new_y)
        
        return {
            'x': new_x if can_move else self.x,
            'y': new_y if can_move else self.y,
            'angle': new_angle,
            'current_target': new_target if can_move and reached_target else self.current_target,
            'moved': can_move,
            'elapsed_time': elapsed_time
        }
    
    def apply_movement(self, movement_data):
        if isinstance(self, SupportsCollisionFreeZones) and self.is_exiting_zone() and not self.is_in_zone():
            self.exiting = None
    
        # Apply calculated position
        if movement_data['moved']:
            self.x = movement_data['x']
            self.y = movement_data['y']
            self.angle = movement_data['angle']
            self.current_target = movement_data['current_target']
            
            # Rotate image
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rotated_width = self.image.get_width()
            self.rotated_height = self.image.get_height()
            
            # Reset cache for hitboxes
            self._cached_hitboxes = None
        
        # Update time for next movement calculation
        self.last_move_time = time.time()
    
    def move(self, obstacles):
        movement_data = self.calculate_next_position(obstacles)
        self.apply_movement(movement_data)

    def can_move(self, obstacles, new_x, new_y):
        can_move = True
        
        if isinstance(self, SupportsCollisionFreeZones) and self.is_in_zone():
            if (self.is_exiting_zone()):
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
                if self.is_exiting_zone() and self.get_current_zone() == obstacle.get_current_zone():
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
        
        # Uncomment to debug hitboxes
        # for hitbox in self.hitboxes():
        #     hitbox_x, hitbox_y = scale_to_display(hitbox.x, hitbox.y)
        #     hitbox_width, hitbox_height = scale_to_display(hitbox.width, hitbox.height)
        #     pygame.draw.rect(screen, (0, 255, 0), (hitbox_x, hitbox_y, hitbox_width, hitbox_height), 2), image_file)