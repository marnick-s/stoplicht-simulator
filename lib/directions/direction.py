from lib.directions.traffic_light import TrafficLight

class Direction():
    def __init__(self, direction_data):
        self.id = direction_data['id']
        self.traffic_lights = []
        self.type = direction_data['type']
        
        for tl in direction_data['traffic_lights']:
            back_sensor_position = tl.get('back_sensor_position', None)
            
            traffic_light = TrafficLight(
                tl['id'],
                tl['traffic_light_position'],
                tl['front_sensor_position'],
                self.type,
                back_sensor_position,
                tl['approach_direction'],
            )
            
            self.traffic_lights.append(traffic_light)
            
    def draw(self, connected):
        for traffic_light in self.traffic_lights:
            traffic_light.draw(connected)