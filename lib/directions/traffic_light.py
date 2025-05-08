import pygame
from lib.collidable_object import CollidableObject, Hitbox
from lib.directions.sensor import Sensor
from lib.enums.traffic_light_colors import TrafficLightColors
from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class TrafficLight(CollidableObject):
    @property
    def id(self):
        return self._id

    def __init__(self, id, traffic_light_position, front_sensor_position, type, back_sensor_position=None, approach_direction=None):
        self._id = id
        self.traffic_light_position = Coordinate(*traffic_light_position)
        self.front_sensor_position = Coordinate(*front_sensor_position)
        self.traffic_light_status = TrafficLightColors.RED
        self.approach_direction = approach_direction
        self.type = type
    
        self.front_sensor = Sensor(front_sensor_position, approach_direction=approach_direction)
        
        self.back_sensor = None
        if back_sensor_position is not None:
            self.back_sensor_position = Coordinate(*back_sensor_position)
            self.back_sensor = Sensor(back_sensor_position, approach_direction=approach_direction)
        
        self.get_sprite()

        self._cached_hitboxes = None

    def get_sprite(self):
        if (self.type == 'pedestrian' or self.type == 'bike'):
            sprite_size = scale_to_display(6, 10)
            green_light_img = pygame.image.load('assets/lights/groen-pedestrian.webp').convert_alpha()
            self.green_light_img = pygame.transform.scale(green_light_img, sprite_size)
            orange_light_img = pygame.image.load('assets/lights/rood-pedestrian.webp').convert_alpha()
            self.orange_light_img = pygame.transform.scale(orange_light_img, sprite_size)
            red_light_img = pygame.image.load('assets/lights/rood-pedestrian.webp').convert_alpha()
            self.red_light_img = pygame.transform.scale(red_light_img, sprite_size)
        else:
            sprite_size = scale_to_display(6, 14)
            green_light_img = pygame.image.load('assets/lights/groen.webp').convert_alpha()
            self.green_light_img = pygame.transform.scale(green_light_img, sprite_size)
            orange_light_img = pygame.image.load('assets/lights/oranje.webp').convert_alpha()
            self.orange_light_img = pygame.transform.scale(orange_light_img, sprite_size)
            red_light_img = pygame.image.load('assets/lights/rood.webp').convert_alpha()
            self.red_light_img = pygame.transform.scale(red_light_img, sprite_size)

    def hitboxes(self):
        if self._cached_hitboxes is None or self._has_changed:
            if (self.type == 'car'):
                width = 6
                height = 6
            else:
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
        if vehicle_direction != self.approach_direction:
            return False
        return self.traffic_light_status != TrafficLightColors.GREEN

    def update(self, color):
        self.traffic_light_status = TrafficLightColors(color)
        self._has_changed = True

    def draw(self, connected):
        self.front_sensor.draw()
        if self.back_sensor is not None:
            self.back_sensor.draw()
            
        if not connected:
            tf_sprite = self.orange_light_img
        else:
            tf_sprite = self.red_light_img
            if self.traffic_light_status == TrafficLightColors.GREEN:
                tf_sprite = self.green_light_img
            elif self.traffic_light_status == TrafficLightColors.ORANGE:
                tf_sprite = self.orange_light_img

        # Bereken sprite positie zodat hij gecentreerd staat op het middelpunt
        sprite_width, sprite_height = self.green_light_img.get_size()
        center_x, center_y = scale_to_display(self.traffic_light_position.x, self.traffic_light_position.y)
        draw_x = center_x - sprite_width // 2
        draw_y = center_y - sprite_height // 2
        screen.blit(tf_sprite, (draw_x, draw_y))

        # rectangle_size = scale_to_display(self.hitboxes()[0].height, self.hitboxes()[0].width)
        # screen.fill(tf_color, (x, y, *rectangle_size))