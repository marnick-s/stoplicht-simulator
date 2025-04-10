from lib.directions.direction import Direction
from lib.enums.topics import Topics
from lib.vehicles.vehicle_spawner import VehicleSpawner

class Simulation:
    def __init__(self, config, messenger):
        self.vehicles = []
        self.config = config
        self.messenger = messenger
        self.directions = self.load_directions(config)
        self.vehicle_spawner = VehicleSpawner(config)


    def load_directions(self, config):
        directions = []
        for direction_data in config['directions']:
            directions.append(Direction(direction_data))
        return directions


    def update(self):
        self.vehicle_spawner.create_new_vehicles(self.vehicles)
        self.update_traffic_lights()
        self.vehicles[:] = [v for v in self.vehicles if not v.has_finished()] # Remove finished vehicles
        obstacles = self.vehicles + [light for d in self.directions for light in d.traffic_lights]
        for vehicle in self.vehicles:
            vehicle.move(obstacles)
        self.check_occupied_sensors()


    def update_traffic_lights(self):
        received_data = self.messenger.received_data
        if not received_data:
            return 
        for direction in self.directions:
            for traffic_light in direction.traffic_lights:
                sensor_id = f"{direction.id}.{traffic_light.id}"
                if sensor_id in received_data:
                    new_color = received_data[sensor_id]
                    traffic_light.update(new_color)


    def check_occupied_sensors(self):
        sensorData = {}
        for direction in self.directions:
            for traffic_light in direction.traffic_lights:
                sensor_id = f"{direction.id}.{traffic_light.id}"
                sensorData[sensor_id] = {"voor": False, "achter": False}

        for vehicle in self.vehicles:
            for direction in self.directions:
                for traffic_light in direction.traffic_lights:
                    status = vehicle.is_occupying_sensor(traffic_light)
                    if status != 0:
                        sensor_id = f"{direction.id}.{traffic_light.id}"
                        if status == 2:
                            sensorData[sensor_id]["achter"] = True
                        else:
                            sensorData[sensor_id]["voor"] = True

        self.messenger.send(Topics.SENSORS_UPDATE.value, sensorData)


    def draw(self):
        for vehicle in self.vehicles:
            vehicle.draw()
        for direction in self.directions:
            direction.draw()