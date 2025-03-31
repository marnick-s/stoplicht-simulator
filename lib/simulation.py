import pygame
from lib.directions.direction import Direction
from lib.enums.topics import Topics
from lib.vehicles.boat import Boat
from lib.vehicles.car import Car

class Simulation:
    vehicle_classes = {
        "car": Car,
        "boat": Boat
    }

    def __init__(self, config, messenger):
        self.vehicles = []
        self.config = config
        self.messenger = messenger
        self.directions = self.load_directions(config)
        self.spawn_timers = {tuple(route['path'][0]): 0 for route in config['routes']}
        self.last_time = pygame.time.get_ticks()

    def load_directions(self, config):
        directions = []
        for direction_data in config['directions']:
            directions.append(Direction(direction_data))
        return directions

    def create_new_vehicles(self):
        current_time = pygame.time.get_ticks()

        for route in self.config['routes']:
            spawn_interval = 60 / route['vehicles_per_minute'] * 1000 if route['vehicles_per_minute'] > 0 else float('inf')
            elapsed_time = current_time - self.last_time
            self.spawn_timers[tuple(route['path'][0])] += elapsed_time

            vehicle_class = self.vehicle_classes.get(route['vehicle_type'])

            if self.spawn_timers[tuple(route['path'][0])] >= spawn_interval:
                self.spawn_timers[tuple(route['path'][0])] = 0
                self.vehicles.append(vehicle_class(route['path']))

        self.last_time = current_time

    def update(self):
        self.create_new_vehicles()
        self.update_traffic_lights()
        self.vehicles = [v for v in self.vehicles if not v.has_finished()] # Remove finished vehicles
        for vehicle in self.vehicles:
            obstacles = self.vehicles + [light for d in self.directions for light in d.traffic_lights]
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
            direction, traffic_light, back_sensor = vehicle.is_occupying_sensor(self.directions)
            if direction is not None and traffic_light is not None:
                sensor_id = f"{direction.id}.{traffic_light.id}"
                if sensor_id not in sensorData:
                    sensorData[sensor_id] = {"voor": False, "achter": False}

                if back_sensor:
                    sensorData[sensor_id]["achter"] = True
                else:
                    sensorData[sensor_id]["voor"] = True

        self.messenger.send(Topics.SENSORS_UPDATE, sensorData)

    def draw(self):
        for vehicle in self.vehicles:
            vehicle.draw()
        for direction in self.directions:
            direction.draw()