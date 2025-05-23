from lib.directions.traffic_light import TrafficLight

class Direction:
    """
    Represents a traffic direction containing one or more traffic lights.
    Responsible for creating and drawing associated traffic lights.
    """

    def __init__(self, direction_data, bridge_out_of_service):
        """
        Initialize the Direction object with traffic lights based on provided data.

        Args:
            direction_data (dict): Configuration data including ID, type, and traffic lights.
        """
        self.id = direction_data['id']
        self.traffic_lights = []
        self.type = direction_data['type']
        
        # Initialize all traffic lights for this direction
        for tl in direction_data['traffic_lights']:
            back_sensor_position = tl.get('back_sensor_position', None)
            controls_barrier = self.id in [41, 42, 51, 52, 53, 54]

            traffic_light = TrafficLight(
                tl['id'],
                tl['traffic_light_position'],
                tl['front_sensor_position'],
                self.type,
                bridge_out_of_service,
                back_sensor_position,
                tl['approach_direction'],
                controls_barrier
            )

            self.traffic_lights.append(traffic_light)
            
    def draw(self):
        """
        Draw all traffic lights in this direction.

        Args:
            connected (bool): Indicates whether the system is connected and operational.
        """
        for traffic_light in self.traffic_lights:
            traffic_light.draw()
