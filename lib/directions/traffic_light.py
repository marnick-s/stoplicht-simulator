import pygame
import time
from lib.collidable_object import CollidableObject, Hitbox
from lib.directions.sensor import Sensor
from lib.enums.traffic_light_colors import TrafficLightColors
from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class TrafficLight(CollidableObject):
    """
    Represents a traffic light object with optional front and back sensors,
    and a visual status based on the current light color.
    """

    @property
    def id(self):
        return self._id

    def __init__(self, id, traffic_light_position, front_sensor_position, type, bridge_out_of_service, back_sensor_position=None, approach_direction=None, controls_barrier=False):
        """
        Initialize a traffic light with sensor(s) and visual configuration.

        Args:
            id (str): Identifier for the traffic light.
            traffic_light_position (tuple): Coordinate of the traffic light.
            front_sensor_position (tuple): Coordinate of the front sensor.
            type (str): Type of the light (e.g., 'car', 'pedestrian').
            back_sensor_position (tuple, optional): Optional back sensor coordinate.
            approach_direction (str, optional): Direction vehicles approach from.
            controls_barrier (bool): Whether this traffic light controls a barrier.
        """
        self._id = id
        self.traffic_light_position = Coordinate(*traffic_light_position)
        self.front_sensor_position = Coordinate(*front_sensor_position)
        self.traffic_light_status = TrafficLightColors.RED
        self.previous_traffic_light_status = TrafficLightColors.RED
        self.approach_direction = approach_direction
        self.type = type
        self.controls_barrier = controls_barrier
        self.bridge_out_of_service = bridge_out_of_service
        self.light_initialized = False
        
        self.is_changing_to_green = False
        self.green_change_time = 0
        self.barrier_delay = 5  # Delay in seconds for the barrier to open, when applicable

        # Initialize sensors
        self.front_sensor = Sensor(front_sensor_position, approach_direction=approach_direction)
        self.back_sensor = None
        if back_sensor_position is not None:
            self.back_sensor_position = Coordinate(*back_sensor_position)
            self.back_sensor = Sensor(back_sensor_position, approach_direction=approach_direction)

        self.get_sprite()
        self._cached_hitboxes = None

    def get_sprite(self):
        """
        Load and scale the correct sprites based on the traffic light type.
        """
        if self.type in ('pedestrian', 'bike'):
            sprite_size = scale_to_display(6, 10)
            green_light_img = pygame.image.load('assets/lights/small/groen.webp').convert_alpha()
            orange_light_img = pygame.image.load('assets/lights/small/rood.webp').convert_alpha()
            red_light_img = pygame.image.load('assets/lights/small/rood.webp').convert_alpha()
        else:
            sprite_size = scale_to_display(6, 14)
            if self.type == 'boat':
                green_light_img = pygame.image.load('assets/lights/boat/groen.webp').convert_alpha()
                if self.bridge_out_of_service:
                    orange_light_img = pygame.image.load('assets/lights/boat/gesloten.webp').convert_alpha()
                    red_light_img = pygame.image.load('assets/lights/boat/gesloten.webp').convert_alpha()
                else:
                    orange_light_img = pygame.image.load('assets/lights/boat/rood.webp').convert_alpha()
                    red_light_img = pygame.image.load('assets/lights/boat/rood.webp').convert_alpha()
            else:
                # Default to car type
                green_light_img = pygame.image.load('assets/lights/car/groen.webp').convert_alpha()
                orange_light_img = pygame.image.load('assets/lights/car/oranje.webp').convert_alpha()
                red_light_img = pygame.image.load('assets/lights/car/rood.webp').convert_alpha()

        self.green_light_img = pygame.transform.scale(green_light_img, sprite_size)
        self.orange_light_img = pygame.transform.scale(orange_light_img, sprite_size)
        self.red_light_img = pygame.transform.scale(red_light_img, sprite_size)

    def hitboxes(self):
        """
        Return the collision hitbox of the traffic light.
        """
        if self._cached_hitboxes is None:
            size = 6 if self.type in ('pedestrian', 'bike') else 8
            self._cached_hitboxes = [Hitbox(
                x=self.traffic_light_position.x - size / 2,
                y=self.traffic_light_position.y - size / 2,
                width=size,
                height=size,
            )]
        return self._cached_hitboxes

    def can_collide(self, vehicle_direction, vehicle_type=None):
        """
        Determine if a vehicle can currently collide with the light based on direction and status.

        Args:
            vehicle_direction (str): Direction of the approaching vehicle.
            vehicle_type (str, optional): Type of the vehicle (not used here).

        Returns:
            bool: True if the vehicle is blocked by the light, False if allowed.
        """
        if vehicle_direction != self.approach_direction:
            return False
        return self.traffic_light_status != TrafficLightColors.GREEN

    def update(self, color):
        """
        Update the light's color.

        Args:
            color (str): New color value (must match TrafficLightColors).
        """
        if self.light_initialized and color != self.previous_traffic_light_status.value and self.controls_barrier and color == TrafficLightColors.GREEN.value:
            # Start the delay so the barrier can open beforehand
            self.is_changing_to_green = True
            self.green_change_time = time.time() + self.barrier_delay
        elif not self.is_changing_to_green:
            # For other traffic lights, update directly
            self.traffic_light_status = TrafficLightColors(color)

        if self.traffic_light_status == TrafficLightColors.GREEN:
            self.light_initialized = True
        self.previous_traffic_light_status = TrafficLightColors(color)
        
    def process_delayed_changes(self):
        """
        Process any delayed color changes (should be called in game loop).
        """
        if self.is_changing_to_green and time.time() >= self.green_change_time:
            self.is_changing_to_green = False
            self.traffic_light_status = TrafficLightColors.GREEN

    def draw(self):
        """
        Draw the traffic light and sensors on the screen.

        Args:
            connected (bool): If False, show orange light regardless of current color.
        """
        # Process any delayed changes before drawing
        self.process_delayed_changes()
            
        self.front_sensor.draw()
        if self.back_sensor is not None:
            self.back_sensor.draw()

        # # Select appropriate sprite based on status
        tf_sprite = self.red_light_img
        if self.traffic_light_status == TrafficLightColors.GREEN:
            tf_sprite = self.green_light_img
        elif self.traffic_light_status == TrafficLightColors.ORANGE:
            tf_sprite = self.orange_light_img

        # # Center the sprite on the traffic light position
        sprite_width, sprite_height = self.green_light_img.get_size()
        center_x, center_y = scale_to_display(self.traffic_light_position.x, self.traffic_light_position.y)
        draw_x = center_x - sprite_width // 2
        draw_y = center_y - sprite_height // 2
        screen.blit(tf_sprite, (draw_x, draw_y))

        # hitboxes = self.hitboxes()
        # for hitbox in hitboxes:
        #     # Convert hitbox to screen coordinates
        #     x, y = scale_to_display(hitbox.x, hitbox.y)
        #     width, height = scale_to_display(hitbox.width, hitbox.height)
            
        #     # Draw rectangle for hitbox (using red color with some transparency)
        #     pygame.draw.rect(screen, (255, 0, 0, 128), (x, y, width, height), 1)