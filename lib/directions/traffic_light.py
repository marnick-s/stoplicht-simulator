from enum import Enum
from lib.collidable_object import CollidableObject, Hitbox
from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class TrafficLightColor(Enum):
    RED = "rood"
    GREEN = "groen"
    ORANGE = "oranje"

class TrafficLight(CollidableObject):
    @property
    def id(self):
        return self._id

    def __init__(self, id, traffic_light_position, front_sensor_position, back_sensor_position):
        self._id = id
        self.traffic_light_position = Coordinate(*traffic_light_position)
        self.front_sensor_position = Coordinate(*front_sensor_position)
        self.back_sensor_position = Coordinate(*back_sensor_position)
        self.traffic_light_status = TrafficLightColor.RED

    def hitbox(self):
        return Hitbox(
            x=self.traffic_light_position.x,
            y=self.traffic_light_position.y,
            width=1,
            height=1,
        )

    def can_collide(self):
        if self.traffic_light_status == TrafficLightColor.GREEN:
            return False
        return True

    def update(self, color):
        self.traffic_light_status = color

    def draw(self):
        front_sensor_x, front_sensor_y = scale_to_display(self.front_sensor_position.x, self.front_sensor_position.y)
        green_color = (0, 255, 0)
        rectangle_size = (10, 10)
        screen.fill(green_color, (front_sensor_x, front_sensor_y, *rectangle_size))