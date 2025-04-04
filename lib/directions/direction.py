from lib.directions.traffic_light import TrafficLight

class Direction():
    def __init__(self, direction_data):
        self.id = direction_data['id']
        self.approach_direction = direction_data['approach_direction']
        self.traffic_lights = [
            TrafficLight(
                tl['id'],
                tl['traffic_light_position'],
                tl['front_sensor_position'],
                tl['back_sensor_position'],
                self.approach_direction
            ) for tl in direction_data['traffic_lights']
        ]        

    def draw(self):
        for traffic_light in self.traffic_lights:
            traffic_light.draw()