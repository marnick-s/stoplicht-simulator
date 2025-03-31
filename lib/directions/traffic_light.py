from lib.collidable_object import CollidableObject, Hitbox
from lib.enums.traffic_light_colors import TrafficLightColors
from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class TrafficLight(CollidableObject):
    @property
    def id(self):
        return self._id

    def __init__(self, id, traffic_light_position, front_sensor_position, back_sensor_position):
        self._id = id
        self.traffic_light_position = Coordinate(*traffic_light_position)
        self.front_sensor_position = Coordinate(*front_sensor_position)
        self.back_sensor_position = Coordinate(*back_sensor_position)
        self.traffic_light_status = TrafficLightColors.RED

    def hitbox(self):
        return Hitbox(
            x=self.traffic_light_position.x,
            y=self.traffic_light_position.y,
            width=10,
            height=10,
        )

    def can_collide(self):
        if self.traffic_light_status == TrafficLightColors.GREEN:
            return False
        return True

    def update(self, color):
        self.traffic_light_status = TrafficLightColors(color)

    def draw(self):
        front_sensor_x, front_sensor_y = scale_to_display(self.front_sensor_position.x, self.front_sensor_position.y)
        green_color = (0, 0, 0)
        rectangle_size = (10, 10)
        screen.fill(green_color, (front_sensor_x, front_sensor_y, *rectangle_size))
        
        tf_color = (255, 0, 0)
        if (self.traffic_light_status == TrafficLightColors.GREEN):
            tf_color = (0, 255, 0)
        elif (self.traffic_light_status == TrafficLightColors.ORANGE):
            tf_color = (255, 255, 0)

        x, y = scale_to_display(self.hitbox().x, self.hitbox().y)
        rectangle_size2 = (self.hitbox().height, self.hitbox().width)
        screen.fill(tf_color, (x, y, *rectangle_size2))