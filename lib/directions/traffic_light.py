import pygame
from lib.collidable_object import CollidableObject, Hitbox
from lib.enums.traffic_light_colors import TrafficLightColors
from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class TrafficLight(CollidableObject):
    @property
    def id(self):
        return self._id

    def __init__(self, id, traffic_light_position, front_sensor_position, back_sensor_position, approach_direction):
        self._id = id
        self.traffic_light_position = Coordinate(*traffic_light_position)
        self.front_sensor_position = Coordinate(*front_sensor_position)
        self.back_sensor_position = Coordinate(*back_sensor_position)
        self.traffic_light_status = TrafficLightColors.RED
        self.approach_direction = approach_direction

        sprite_size = (20, 48)

        green_light_img = pygame.image.load('assets/lights/groen.webp').convert_alpha()
        self.green_light_img = pygame.transform.scale(green_light_img, sprite_size)

        orange_light_img = pygame.image.load('assets/lights/oranje.webp').convert_alpha()
        self.orange_light_img = pygame.transform.scale(orange_light_img, sprite_size)

        red_light_img = pygame.image.load('assets/lights/rood.webp').convert_alpha()
        self.red_light_img = pygame.transform.scale(red_light_img, sprite_size)

    def hitboxes(self):
        return [Hitbox(
            x=self.traffic_light_position.x,
            y=self.traffic_light_position.y,
            width=10,
            height=10,
        )]

    def can_collide(self, vehicle_direction):
        if vehicle_direction != self.approach_direction:
            return False
        return self.traffic_light_status != TrafficLightColors.GREEN

    def update(self, color):
        self.traffic_light_status = TrafficLightColors(color)

    def draw(self):
        front_sensor_x, front_sensor_y = scale_to_display(self.front_sensor_position.x, self.front_sensor_position.y)
        green_color = (0, 0, 0)
        rectangle_size = scale_to_display(10, 10)
        screen.fill(green_color, (front_sensor_x, front_sensor_y, *rectangle_size))
        
        tf_color = (255, 0, 0)
        tf_sprite = self.green_light_img
        if (self.traffic_light_status == TrafficLightColors.GREEN):
            tf_color = (0, 255, 0)
            tf_sprite = self.red_light_img
        elif (self.traffic_light_status == TrafficLightColors.ORANGE):
            tf_color = (255, 255, 0)
            tf_sprite = self.orange_light_img

        x, y = scale_to_display(self.hitboxes()[0].x, self.hitboxes()[0].y)
        screen.blit(tf_sprite, (x + 30, y - 18))
        # rectangle_size2 = scale_to_display(self.hitboxes()[0].height, self.hitboxes()[0].width)
        # screen.fill(tf_color, (x, y, *rectangle_size2))