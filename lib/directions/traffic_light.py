import pygame
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

    def __init__(self, id, traffic_light_position, front_sensor_position, type, bridge_closed, back_sensor_position=None, approach_direction=None):
        """
        Initialize a traffic light with sensor(s) and visual configuration.

        Args:
            id (str): Identifier for the traffic light.
            traffic_light_position (tuple): Coordinate of the traffic light.
            front_sensor_position (tuple): Coordinate of the front sensor.
            type (str): Type of the light (e.g., 'car', 'pedestrian').
            back_sensor_position (tuple, optional): Optional back sensor coordinate.
            approach_direction (str, optional): Direction vehicles approach from.
        """
        self._id = id
        self.traffic_light_position = Coordinate(*traffic_light_position)
        self.front_sensor_position = Coordinate(*front_sensor_position)
        self.traffic_light_status = TrafficLightColors.RED
        self.approach_direction = approach_direction
        self.type = type
        self.bridge_closed = bridge_closed

        # Initialize sensors
        self.front_sensor = Sensor(front_sensor_position, approach_direction=approach_direction)
        self.back_sensor = None
        if back_sensor_position is not None:
            self.back_sensor_position = Coordinate(*back_sensor_position)
            self.back_sensor = Sensor(back_sensor_position, approach_direction=approach_direction)

        self.get_sprite()
        self._cached_hitboxes = None
        self._has_changed = True

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
        if self._cached_hitboxes is None or self._has_changed:
            width = 6
            height = 6
            self._cached_hitboxes = [Hitbox(
                x=self.traffic_light_position.x - width / 2,
                y=self.traffic_light_position.y - height / 2,
                width=width,
                height=height,
            )]
            self._has_changed = False
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
        self.traffic_light_status = TrafficLightColors(color)
        self._has_changed = True

    def draw(self, connected):
        """
        Draw the traffic light and sensors on the screen.

        Args:
            connected (bool): If False, show orange light regardless of current color.
        """
        self.front_sensor.draw()
        if self.back_sensor is not None:
            self.back_sensor.draw()

        if self.type == 'boat' and self.bridge_closed:
            # Show red light for boats when the bridge is closed
            tf_sprite = self.red_light_img
        else:
            # Select appropriate sprite based on status
            tf_sprite = self.red_light_img
            if self.traffic_light_status == TrafficLightColors.GREEN:
                tf_sprite = self.green_light_img
            elif self.traffic_light_status == TrafficLightColors.ORANGE:
                tf_sprite = self.orange_light_img

        # Center the sprite on the traffic light position
        sprite_width, sprite_height = self.green_light_img.get_size()
        center_x, center_y = scale_to_display(self.traffic_light_position.x, self.traffic_light_position.y)
        draw_x = center_x - sprite_width // 2
        draw_y = center_y - sprite_height // 2
        screen.blit(tf_sprite, (draw_x, draw_y))
