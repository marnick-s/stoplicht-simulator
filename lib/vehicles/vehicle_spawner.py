import random
import pygame

from lib.vehicles.boat import Boat
from lib.vehicles.car import Car
from lib.vehicles.path import Path
from lib.vehicles.pedestrian import Pedestrian

class VehicleSpawner:
    vehicle_classes = {
        "car": Car,
        "boat": Boat,
        "pedestrian": Pedestrian,
    }

    def __init__(self, config, traffic_level="rustig"):
        self.config = config
        self.traffic_level = traffic_level
        current_time = pygame.time.get_ticks()
        self.next_spawn_times = {}

        for route in config['routes']:
            vehicles_per_minute = self.get_vehicles_per_minute(route)
            delay = random.expovariate(vehicles_per_minute / 60) * 1000 if vehicles_per_minute > 0 else float('inf')
            self.next_spawn_times[tuple(route['name'])] = current_time + delay

    def get_vehicles_per_minute(self, route):
        if self.traffic_level == "rustig":
            return route.get("vehicles_per_minute_rustig", 0)
        elif self.traffic_level == "spits":
            return route.get("vehicles_per_minute_spits", 0)
        elif self.traffic_level == "stress":
            return max(
                route.get("vehicles_per_minute_rustig", 0),
                route.get("vehicles_per_minute_spits", 0)
            )
        return 0

    def create_new_vehicles(self, vehicles):
        current_time = pygame.time.get_ticks()

        for route in self.config['routes']:
            vehicles_per_minute = self.get_vehicles_per_minute(route)

            if vehicles_per_minute <= 0:
                continue

            key = tuple(route['name'])
            if current_time >= self.next_spawn_times[key]:
                vehicle_class = self.vehicle_classes.get(route['vehicle_type'])
                path = Path(route["path"], self.config["route_components"])
                new_vehicle = vehicle_class(path.get_pretty_path())

                # 3) Alleen toevoegen als er géén collision is
                if not any(new_vehicle.collides_with(ev) for ev in vehicles):
                    vehicles.append(new_vehicle)

                # 4) Plan de volgende spawn pas als er wél een positieve rate is
                delay = random.expovariate(vehicles_per_minute / 60) * 1000
                self.next_spawn_times[key] = current_time + delay
