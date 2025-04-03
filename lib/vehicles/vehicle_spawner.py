import random
import pygame

from lib.vehicles.boat import Boat
from lib.vehicles.car import Car
from lib.vehicles.path import Path

class VehicleSpawner:
    vehicle_classes = {
        "car": Car,
        "boat": Boat
    }
        

    def __init__(self, config):
        self.config = config
        current_time = pygame.time.get_ticks()
        # Voor elke route berekenen we een eerste spawn-tijd.
        self.next_spawn_times = {}
        for route in config['routes']:
            if route['vehicles_per_minute'] > 0:
                # Random wachttijd in milliseconden: gemiddelde = 60000 / vehicles_per_minute
                delay = random.expovariate(route['vehicles_per_minute'] / 60) * 1000
            else:
                delay = float('inf')
            self.next_spawn_times[tuple(route['path'][0])] = current_time + delay

    def create_new_vehicles(self, vehicles):
        current_time = pygame.time.get_ticks()
        
        for route in self.config['routes']:
            key = tuple(route['path'][0])
            
            if current_time >= self.next_spawn_times[key]:
                vehicle_class = self.vehicle_classes.get(route['vehicle_type'])
                path = Path(route["path"], self.config["route_components"])
                new_vehicle = vehicle_class(path.get_pretty_path())
                
                # Voorkom dat voertuigen in elkaar spawnen
                if not any(new_vehicle.collides_with(existing_vehicle) for existing_vehicle in vehicles):
                    vehicles.append(new_vehicle)
                else:
                    # Optioneel: log dat een spawn is overgeslagen vanwege collision
                    pass

                # Bepaal de volgende spawn-tijd met een random interval (gemiddelde = 60000 / vehicles_per_minute)
                if route['vehicles_per_minute'] > 0:
                    delay = random.expovariate(route['vehicles_per_minute'] / 60) * 1000
                else:
                    delay = float('inf')
                self.next_spawn_times[key] = current_time + delay