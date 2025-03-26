import pygame
from lib.boat import Boat
from lib.screen import WIDTH, HEIGHT
from lib.car import Car

class Simulation:
    vehicle_classes = {
        "car": Car,
        "boat": Boat
    }

    def __init__(self, config):
        self.vehicles = []
        self.config = config
        self.spawn_timers = {tuple(route['path'][0]): 0 for route in config['routes']}
        self.last_time = pygame.time.get_ticks()

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
            vehicle.move()

    def draw(self):
        for vehicle in self.vehicles:
            vehicle.draw()