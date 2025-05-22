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
    """
    Represents a vehicle moving along a defined path with collision detection and
    smooth time-based movement. Supports image loading, rotation, hitbox calculation,
    and collision-free zone handling.
    """
    __slots__ = ('path', 'id', 'current_target', 'x', 'y', 'speed', 'vehicle_type_string', 
                 'original_image', 'sprite_width', 'sprite_height', 'angle', 'image', 
                 'rotated_width', 'rotated_height', '_cached_hitboxes', '_last_position', 
                 '_last_angle', 'last_move_time')
    
    # Class variables shared by all instances
    collision_free_zones = []
    last_update_time = time.time()
    
    # Pre-load and cache images to avoid repeated disk access
    _image_cache = {}

    def __init__(self, id, path, speed, vehicle_type_string):
        """
        Initialize the vehicle with an ID, path to follow, speed (units per second),
        and vehicle type to load corresponding sprite images.

        Args:
            id (any): Unique identifier for the vehicle.
            path (list of (x,y)): List of waypoints the vehicle will follow.
            speed (float): Movement speed in units per second.
            vehicle_type_string (str): Folder name for vehicle sprite images.
        """
        self.path = path
        self.id = id
        self.current_target = 0  # Index of the next waypoint in the path
        self.x, self.y = self.path[self.current_target]
        self.speed = speed  # Units per second
        self.vehicle_type_string = vehicle_type_string
        
        # Load a random sprite image from the vehicle's asset folder with dimension extraction
        self.original_image, self.sprite_width, self.sprite_height = self.load_random_image_with_dimensions(
            "assets/vehicles/" + self.vehicle_type_string
        )
        
        self.angle = 0  # Current rotation angle in degrees
        self.image = self.original_image.copy()
        self.rotated_width = self.sprite_width
        self.rotated_height = self.sprite_height
        
        # Cache for hitboxes to improve performance by avoiding recalculations
        self._cached_hitboxes = None
        self._last_position = (self.x, self.y)
        self._last_angle = self.angle
        
        # Timestamp of last movement update for smooth frame-independent movement
        self.last_move_time = time.time()

    def after_create(self):
        """Placeholder method to be optionally overridden by subclasses."""
        pass
    
    @classmethod
    def _load_image_from_file(cls, image_path):
        """Load an image from file with caching for better performance."""
        if image_path not in cls._image_cache:
            cls._image_cache[image_path] = pygame.image.load(image_path).convert_alpha()
        return cls._image_cache[image_path]
    
    def load_random_image_with_dimensions(self, folder):
        """
        Loads a random .webp image from a given folder, extracts sprite dimensions
        from the filename (format: WIDTHxHEIGHT[-index].webp), and scales it.

        Args:
            folder (str): Path to the folder containing sprite images.

        Returns:
            tuple: (scaled pygame.Surface, width, height)
        """
        # Use class variable to avoid redoing file listing for same folders
        if not hasattr(Vehicle, '_folder_image_files'):
            Vehicle._folder_image_files = {}
            
        if folder not in Vehicle._folder_image_files:
            Vehicle._folder_image_files[folder] = [
                f for f in os.listdir(folder) if f.endswith('.webp')
            ]
            
        image_files = Vehicle._folder_image_files[folder]
        if not image_files:
            raise ValueError(f"Geen WebP-afbeeldingen gevonden in de map: {folder}")
        
        image_file = random.choice(image_files)
        
        # Use pre-compiled regex pattern for better performance
        if not hasattr(Vehicle, '_dimensions_pattern'):
            Vehicle._dimensions_pattern = re.compile(r'(\d+)x(\d+)(?:-\d+)?\.webp$')
            
        dimensions_match = Vehicle._dimensions_pattern.search(image_file)
        if dimensions_match:
            sprite_width = int(dimensions_match.group(1))
            sprite_height = int(dimensions_match.group(2))
        else:
            # Fallback dimensions if pattern does not match
            sprite_width = 40
            sprite_height = 40
        
        image_path = os.path.join(folder, image_file)
        image = self._load_image_from_file(image_path)
        scaled_image = self.scale_image(image, sprite_width, sprite_height)
        
        return scaled_image, sprite_width, sprite_height

    def scale_image(self, image, width, height):
        """
        Scale the given image to display coordinates based on width and height.

        Args:
            image (pygame.Surface): The original image to scale.
            width (int): Target width.
            height (int): Target height.

        Returns:
            pygame.Surface: Scaled image surface.
        """
        # Cache scaled images based on dimensions
        cache_key = (id(image), width, height)
        if not hasattr(Vehicle, '_scaled_image_cache'):
            Vehicle._scaled_image_cache = {}
            
        if cache_key not in Vehicle._scaled_image_cache:
            scaled_dims = scale_to_display(width, height)
            Vehicle._scaled_image_cache[cache_key] = pygame.transform.scale(image, scaled_dims)
            
        return Vehicle._scaled_image_cache[cache_key]
    
    def hitboxes(self):
        """
        Generate or return cached hitboxes representing the vehicle's collision area.
        Hitboxes are divided along the vehicle's length for more precise collision.

        Returns:
            list of Hitbox: List of hitboxes covering the vehicle.
        """
        # Return cached hitboxes if position and angle haven't changed
        current_pos = (self.x, self.y)
        if self._cached_hitboxes is not None and current_pos == self._last_position and self.angle == self._last_angle:
            return self._cached_hitboxes
        
        # Divide vehicle length into segments for multiple hitboxes
        num_segments = max(round(self.sprite_width / 6), 1)
        margin = 0.4  # Margin to shrink hitboxes slightly inside sprite boundaries
        segment_length = self.sprite_width / num_segments
        vehicle_width = self.sprite_height * (1 - margin)
        
        # Pre-compute angle in radians once (avoid repeated conversions)
        angle_rad = math.radians(self.angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = -math.sin(angle_rad)
        
        # Create hitboxes with list comprehension for better performance
        if num_segments > 1:
            hitboxes = [
                Hitbox(
                    x=self.x + cos_angle * ((i - num_segments / 2 + 0.5) * segment_length) - vehicle_width // 2,
                    y=self.y + sin_angle * ((i - num_segments / 2 + 0.5) * segment_length) - vehicle_width // 2,
                    width=segment_length * (1 - margin),
                    height=vehicle_width
                )
                for i in range(num_segments)
            ]
        else:
            # Simplified case for single hitbox
            hitboxes = [
                Hitbox(
                    x=self.x - vehicle_width // 2,
                    y=self.y - vehicle_width // 2,
                    width=segment_length * (1 - margin),
                    height=vehicle_width
                )
            ]

        # Cache results for performance
        self._cached_hitboxes = hitboxes
        self._last_position = current_pos
        self._last_angle = self.angle
        return hitboxes
    
    def calculate_next_position(self, obstacles):
        """
        Calculate the vehicle's next position along its path based on elapsed time,
        speed, and collision checks with obstacles.

        Args:
            obstacles (list): List of objects to check collisions against.

        Returns:
            dict: Contains updated position, angle, target index, and move status.
        """
        # Handle releasing zone reservation if applicable
        if isinstance(self, SupportsCollisionFreeZones):
            self.release_exiting_if_possible(obstacles)
    
        # If reached the last waypoint, no movement needed
        if self.current_target >= len(self.path) - 1:
            return {
                'x': self.x,
                'y': self.y,
                'speed': self.speed,
                'angle': self.angle,
                'current_target': self.current_target,
                'moved': False  # Vehicle did not move
            }
        
        # Calculate elapsed time since last movement update
        current_time = time.time()
        elapsed_time = min(current_time - self.last_move_time, 0.05) # Clamp to avoid large jumps in time, limited to 20fps
        
        # Target waypoint coordinates
        target_x, target_y = self.path[self.current_target + 1]
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.hypot(dx, dy)  # Faster than **2 and sqrt
        
        if distance <= 0.01:  # Avoid division by zero with small threshold
            distance = 0.01
        
        # Calculate movement distance based on speed and elapsed time
        move_distance = self.speed * elapsed_time
        if move_distance > distance:
            move_distance = distance  # Clamp movement to not overshoot target
        
        # Movement ratio for faster multiplication instead of division
        move_ratio = move_distance / distance
        
        # Compute new position along the path
        new_x = self.x + dx * move_ratio
        new_y = self.y + dy * move_ratio
        
        # Calculate new facing angle based on movement direction (pygame y-axis inverted)
        new_angle = math.degrees(math.atan2(-dy, dx))
        
        # Check if the target waypoint is reached (within half move distance threshold)
        half_move = move_distance * 0.5
        reached_target = (abs(new_x - target_x) < half_move and 
                          abs(new_y - target_y) < half_move)
        
        new_target = self.current_target + (1 if reached_target else 0)
        
        # Validate if the vehicle can move to the new position without collisions
        can_move = self.can_move(obstacles, new_x, new_y)
        
        return {
            'x': new_x if can_move else self.x,
            'y': new_y if can_move else self.y,
            'angle': new_angle,
            'current_target': new_target if can_move else self.current_target,
            'moved': can_move,
            'elapsed_time': elapsed_time
        }
    
    def apply_movement(self, movement_data):
        """
        Update the vehicle's position, angle, and target index based on movement data,
        and rotate the sprite accordingly.

        Args:
            movement_data (dict): Dictionary containing new position, angle, etc.
        """
        if movement_data['moved']:
            self.x = movement_data['x']
            self.y = movement_data['y']
            
            # Only rotate the sprite if the angle has changed significantly
            new_angle = movement_data['angle']
            if abs(self.angle - new_angle) > 0.5:  # Only rotate if angle changed by more than 0.5 degrees
                self.angle = new_angle
                
                # Only regenerate the rotated image when needed
                self.image = pygame.transform.rotate(self.original_image, self.angle)
                self.rotated_width = self.image.get_width()
                self.rotated_height = self.image.get_height()
                
                # Invalidate hitbox cache since angle changed
                self._cached_hitboxes = None
            elif self.x != movement_data['x'] or self.y != movement_data['y']:
                # Position changed but angle didn't - still invalidate cache
                self._cached_hitboxes = None
                
            self.current_target = movement_data['current_target']
        
        # Update the timestamp for the last movement to calculate elapsed time next frame
        self.last_move_time = time.time()
    
    def move(self, obstacles):
        """
        Compute the next valid position and apply it.

        Args:
            obstacles (list): List of obstacles to check collisions against.
        """
        movement_data = self.calculate_next_position(obstacles)
        self.apply_movement(movement_data)

    def can_move(self, obstacles, new_x, new_y):
        """
        Check if the vehicle can move to the specified position without colliding
        with obstacles or violating collision-free zones.

        Args:
            obstacles (list): List of obstacles.
            new_x (float): Proposed new x position.
            new_y (float): Proposed new y position.

        Returns:
            bool: True if movement is allowed, False otherwise.
        """
        # Handle special logic if vehicle supports collision-free zones and is inside one
        if isinstance(self, SupportsCollisionFreeZones) and self.is_in_zone():
            if not self.is_exiting_zone():
                current_zone = self.get_current_zone()

                # Temporarily update position to test collision with zone
                temp_x, temp_y = self.x, self.y
                self.x, self.y = new_x, new_y

                if not self.collides_with(current_zone):
                    # Check if vehicle can exit the zone
                    if self.can_exit_zone(obstacles, new_x, new_y, current_zone.id):
                        self.exiting = current_zone.id
                    else:
                        self.x, self.y = temp_x, temp_y  # Restore position
                        return False
                
                # Restore original position
                self.x, self.y = temp_x, temp_y

        # Check collision with all obstacles at the new position
        temp_x, temp_y = self.x, self.y
        self.x, self.y = new_x, new_y  # Temporarily set to proposed position
        
        # Cache vehicle direction and angle for repeated collision checks
        vehicle_dir = self.get_vehicle_direction()
        collision_ang = self.angle
        
        # Fast path: try to avoid checking every obstacle
        for obstacle in obstacles:
            # Skip collision check if both objects are in the same collision-free zone or vehicle is exiting zone
            if isinstance(self, SupportsCollisionFreeZones) and isinstance(obstacle, SupportsCollisionFreeZones):
                if self.in_same_cf_zone(obstacle) or self.is_exiting_zone():
                    continue
                    
            # Check collision based on hitboxes, direction, and angle
            if self.collides_with(obstacle, vehicle_direction=vehicle_dir, collision_angle=collision_ang):
                self.x, self.y = temp_x, temp_y  # Restore position
                return False
            
        # Restore original position after collision checks
        self.x, self.y = temp_x, temp_y
        return True
        
    def get_vehicle_direction(self):
        """
        Determine the cardinal direction of the vehicle based on its current angle.

        Returns:
            str: One of 'west', 'south', 'north', or 'east' indicating direction.
        """
        # Use cached direction if we've computed it before at this angle
        if not hasattr(self, '_direction_cache'):
            self._direction_cache = {}
            
        if self.angle in self._direction_cache:
            return self._direction_cache[self.angle]
            
        # Compute direction based on angle
        if -45 <= self.angle <= 45:
            direction = 'west'
        elif 45 < self.angle <= 135:
            direction = 'south'
        elif -135 <= self.angle < -45:
            direction = 'north'
        else:
            direction = 'east'
            
        # Cache result
        self._direction_cache[self.angle] = direction
        return direction

    def rotate_to_path(self):
        """
        Rotate the vehicle image to align with the direction of the next path segment.
        Updates the vehicle's angle and rotated sprite dimensions.
        """
        if self.current_target < len(self.path) - 1:
            start_x, start_y = self.path[self.current_target]
            end_x, end_y = self.path[self.current_target + 1]
            
            dx = end_x - start_x
            dy = end_y - start_y
            
            # Calculate angle in degrees (-dy because pygame's y-axis is inverted)
            new_angle = math.degrees(math.atan2(-dy, dx))
            
            # Only rotate if angle has changed significantly
            if abs(self.angle - new_angle) > 0.5:
                self.angle = new_angle
                
                # Rotate the original image and update dimensions
                self.image = pygame.transform.rotate(self.original_image, self.angle)
                self.rotated_width = self.image.get_width()
                self.rotated_height = self.image.get_height()
                
                # Invalidate hitbox cache
                self._cached_hitboxes = None

    def has_finished(self):
        """
        Check if the vehicle has reached the last target in its path.

        Returns:
            bool: True if the vehicle is at or beyond the last path target.
        """
        return self.current_target >= len(self.path) - 1

    def draw(self):
        """ 
        Draw the vehicle's rotated image centered at its current position on the screen.
        """
        screen_x, screen_y = scale_to_display(self.x, self.y)
        draw_x = int(screen_x - self.rotated_width // 2)
        draw_y = int(screen_y - self.rotated_height // 2)
        screen.blit(self.image, (draw_x, draw_y))
        
        # Uncomment below to draw debug rectangles around hitboxes
        # for hitbox in self.hitboxes():
        #     hitbox_x, hitbox_y = scale_to_display(hitbox.x, hitbox.y)
        #     hitbox_width, hitbox_height = scale_to_display(hitbox.width, hitbox.height)
        #     pygame.draw.rect(screen, (0, 255, 0), (hitbox_x, hitbox_y, hitbox_width, hitbox_height), 2)