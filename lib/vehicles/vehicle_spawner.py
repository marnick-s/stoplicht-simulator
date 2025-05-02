import random
import pygame
from lib.vehicles.bike import Bike
from lib.vehicles.boat import Boat
from lib.vehicles.car import Car
from lib.vehicles.bus import Bus
from lib.vehicles.emergency_vehicle import EmergencyVehicle
from lib.vehicles.path import Path
from lib.vehicles.pedestrian import Pedestrian
from lib.vehicles.priority_queue_manager import PriorityQueueManager

class VehicleSpawner:
    vehicle_classes = {
        "car": Car,
        "boat": Boat,
        "pedestrian": Pedestrian,
        "bike": Bike,
        "bus": Bus,
        "emergency_vehicle": EmergencyVehicle
    }

    def __init__(self, config, traffic_level="rustig", messenger=None):
        self.config = config
        self.traffic_level = traffic_level
        self.priority_queue_manager = PriorityQueueManager(messenger)
        current_time = pygame.time.get_ticks()

        self.vehicle_id_counter = 0  # Teller voor unieke voertuig-ID's

        # Initialize spawn timers voor reguliere routes
        self.next_spawn_times = {}
        for route in config['routes']:
            vpm = self.get_vehicles_per_minute(route)
            delay = random.expovariate(vpm / 60) * 1000 if vpm > 0 else float('inf')
            self.next_spawn_times[tuple(route['name'])] = current_time + delay

        # Initialize priority spawn timers
        self.next_bus_spawn_time = current_time + self.get_random_bus_delay()
        self.next_emergency_spawn_time = current_time + self.get_random_emergency_delay()

        # Car routes voor priority spawns
        self.car_routes = [r for r in config['routes'] if r['vehicle_type'] == 'car']

    def assign_id(self, vehicle):
        vehicle.id = self.vehicle_id_counter
        self.vehicle_id_counter += 1

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

    def get_random_bus_delay(self):
        return random.expovariate(1/60) * 1000

    def get_random_emergency_delay(self):
        return random.expovariate(1/120) * 1000

    def get_lane_id_from_route(self, route):
        # print(route)
        name_tuple = route['name']
        if len(name_tuple) >= 2:
            return name_tuple[1]
        return "0.0"

    def spawn_priority_vehicle(self, vehicles, vehicle_type):
        route = random.choice(self.car_routes)

        cls = self.vehicle_classes.get(vehicle_type)
        path = Path(route["path"], self.config["route_components"])
        vehicle = cls(self.vehicle_id_counter, path.get_pretty_path())

        if not any(vehicle.collides_with(v) for v in vehicles):
            self.assign_id(vehicle)
            vehicles.append(vehicle)
            # Notify priority queue manager
            if self.priority_queue_manager and vehicle_type in ("bus", "emergency_vehicle"):
                lane_id = self.get_lane_id_from_route(route)
                self.priority_queue_manager.add(lane_id, vehicle)
            return vehicle
        return None

    def update(self, vehicles, delta_time):
        self.create_new_vehicles(vehicles)
        self.priority_queue_manager.update(delta_time, vehicles)

    def create_new_vehicles(self, vehicles):
        current_time = pygame.time.get_ticks()

        # Spawn reguliere voertuigen
        for route in self.config['routes']:
            vpm = self.get_vehicles_per_minute(route)
            if vpm <= 0:
                continue
            key = tuple(route['name'])
            if current_time >= self.next_spawn_times[key]:
                cls = self.vehicle_classes.get(route['vehicle_type'])
                path = Path(route['path'], self.config["route_components"])
                vehicle = cls(self.vehicle_id_counter, path.get_pretty_path())
                if not any(vehicle.collides_with(v) for v in vehicles):
                    self.assign_id(vehicle)
                    vehicles.append(vehicle)
                delay = random.expovariate(vpm / 60) * 1000
                self.next_spawn_times[key] = current_time + delay

        # Spawn bus
        if self.car_routes and current_time >= getattr(self, 'next_bus_spawn_time', 0):
            if self.spawn_priority_vehicle(vehicles, "bus"):
                self.next_bus_spawn_time = current_time + self.get_random_bus_delay()
            else:
                self.next_bus_spawn_time = current_time + 5000

        # Spawn emergency vehicle
        if self.car_routes and current_time >= getattr(self, 'next_emergency_spawn_time', 0):
            if self.spawn_priority_vehicle(vehicles, "emergency_vehicle"):
                self.next_emergency_spawn_time = current_time + self.get_random_emergency_delay()
            else:
                self.next_emergency_spawn_time = current_time + 5000