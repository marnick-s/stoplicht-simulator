from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class TrafficLight():
    @property
    def id(self):
        return self._id
    
    @property
    def traffic_light_position(self):
        return self._traffic_light_position

    @property
    def front_sensor_position(self):
        return self._front_sensor_position

    @property
    def back_sensor_position(self):
        return self._back_sensor_position

    def __init__(self, id, traffic_light_position, front_sensor_position, back_sensor_position):
        self._id = id
        self._traffic_light_position = Coordinate(*traffic_light_position)
        self._front_sensor_position = Coordinate(*front_sensor_position)
        self._back_sensor_position = Coordinate(*back_sensor_position)
        self.traffic_light_status = 0
        self.front_sensor_occupied = False
        self.back_sensor_occupied = False

    def update(self):
        print("Updating traffic light", self.id)

    def draw(self):
        front_sensor_x, front_sensor_y = scale_to_display(self.front_sensor_position.x, self.front_sensor_position.y)
        green_color = (0, 255, 0)
        rectangle_size = (10, 10)
        screen.fill(green_color, (front_sensor_x, front_sensor_y, *rectangle_size))