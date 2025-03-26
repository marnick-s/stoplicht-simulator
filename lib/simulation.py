import pygame
from lib.directions.direction import Direction
from lib.vehicles.boat import Boat
from lib.vehicles.car import Car

class Simulation:
    vehicle_classes = {
        "car": Car,
        "boat": Boat
    }

    def __init__(self, config):
        self.vehicles = []
        self.config = config
        self.directions = self.load_directions(config)
        self.spawn_timers = {tuple(route['path'][0]): 0 for route in config['routes']}
        self.last_time = pygame.time.get_ticks()

    def load_directions(self, config):
        directions = []
        for direction_data in config['directions']:
            directions.append(Direction(direction_data))
        return directions

    def spawn_vehicles(self):
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
        self.spawn_vehicles()
        for vehicle in self.vehicles:
            vehicle.move(self.vehicles, self.directions, self.occupy_sensor)

    def occupy_sensor(self, direction, traffic_light, back_sensor):
        if back_sensor:
            direction = next(d for d in self.directions if d.id == direction.id)
            traffic_light = next(tl for tl in direction.traffic_lights if tl.id == traffic_light.id)
            traffic_light.back_sensor_occupied = True
        else:
            direction = next(d for d in self.directions if d.id == direction.id)
            traffic_light = next(tl for tl in direction.traffic_lights if tl.id == traffic_light.id)
            traffic_light.front_sensor_occupied = True
            print(f"Sensor occupied: {direction.id} - {traffic_light.id}")

    def draw(self):
        for vehicle in self.vehicles:
            vehicle.draw()
        for direction in self.directions:
            direction.draw()