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
    """
    Responsible for spawning vehicles on predefined routes with varying spawn rates
    based on the current traffic level. Also handles priority vehicles such as buses
    and emergency vehicles.
    """
    vehicle_classes = {
        "car": Car,
        "boat": Boat,
        "pedestrian": Pedestrian,
        "bike": Bike,
        "bus": Bus,
        "emergency_vehicle": EmergencyVehicle
    }

    def __init__(self, config, traffic_level="rustig", messenger=None):
        """
        Initialize the spawner with route config and traffic level.
        
        :param config: Configuration dict containing routes and vehicle types
        :param traffic_level: 'rustig', 'spits', or 'stress'
        :param messenger: Optional messaging system for priority queue communication
        """
        self.config = config
        self.traffic_level = traffic_level
        self.priority_queue_manager = PriorityQueueManager(messenger)
        current_time = pygame.time.get_ticks()

        self.vehicle_id_counter = 0  # Counter for assigning unique vehicle IDs

        # Initialize next spawn times for regular routes
        self.next_spawn_times = {}
        for route in config['routes']:
            vpm = self.get_vehicles_per_interval(route)
            delay = random.expovariate(vpm / 60) * 5000 if vpm > 0 else float('inf')
            self.next_spawn_times[tuple(route['name'])] = current_time + delay

        # Initialize timers for priority vehicles
        self.next_bus_spawn_time = current_time + self.get_random_bus_delay()
        self.next_emergency_spawn_time = current_time + self.get_random_emergency_delay()

        # Filter car routes for possible use with priority vehicles
        self.car_routes = [r for r in config['routes'] if r['vehicle_type'] == 'car']

    def assign_id(self, vehicle):
        """Assign a unique ID to the given vehicle."""
        vehicle.id = self.vehicle_id_counter
        self.vehicle_id_counter += 1

    def get_vehicles_per_interval(self, route):
        """
        Get the number of vehicles to spawn per interval based on the traffic level.
        """
        if self.traffic_level == "rustig":
            return route.get("vehicles_per_interval_rustig", 0)
        elif self.traffic_level == "spits":
            return route.get("vehicles_per_interval_spits", 0)
        elif self.traffic_level == "stress":
            # Double the highest value of rustig and spits under 'stress'
            return max(
                route.get("vehicles_per_interval_rustig", 0),
                route.get("vehicles_per_interval_spits", 0)
            ) * 2
        return 0

    def get_random_bus_delay(self):
        """Return a random delay (in ms) before the next bus spawn using exponential distribution."""
        return random.expovariate(1 / 120) * 1000

    def get_random_emergency_delay(self):
        """Return a random delay (in ms) before the next emergency vehicle spawn using exponential distribution."""
        return random.expovariate(1 / 300) * 1000

    def spawn_priority_vehicle(self, vehicles, vehicle_type):
        """
        Attempt to spawn a priority vehicle (bus/emergency).
        Only spawns if no collisions would occur.

        :param vehicles: Current list of vehicles in the simulation
        :param vehicle_type: Type of vehicle to spawn
        :return: The spawned vehicle or None
        """
        route = random.choice(self.car_routes)

        cls = self.vehicle_classes.get(vehicle_type)
        path = Path(route["path"], self.config["route_components"])
        vehicle = cls(self.vehicle_id_counter, path.get_pretty_path())

        # Ensure the new vehicle does not collide with any existing vehicle
        if not any(vehicle.collides_with(v) for v in vehicles):
            self.assign_id(vehicle)
            vehicle.after_create()
            vehicles.append(vehicle)

            # Register the vehicle in the priority queue
            if self.priority_queue_manager and vehicle_type in ("bus", "emergency_vehicle"):
                lane_id = path.get_associated_lane()
                self.priority_queue_manager.add(lane_id, vehicle)
            return vehicle
        return None

    def update(self, vehicles):
        """
        Called regularly to potentially spawn new vehicles and update the priority queue.
        """
        self.create_new_vehicles(vehicles)
        self.priority_queue_manager.update(vehicles)

    def create_new_vehicles(self, vehicles):
        """
        Handles the logic for spawning new regular and priority vehicles.
        """
        current_time = pygame.time.get_ticks()

        # Spawn regular vehicles
        for route in self.config['routes']:
            vpm = self.get_vehicles_per_interval(route)
            if vpm <= 0:
                continue
            key = tuple(route['name'])
            if current_time >= self.next_spawn_times[key]:
                cls = self.vehicle_classes.get(route['vehicle_type'])
                path = Path(route['path'], self.config["route_components"])
                vehicle = cls(self.vehicle_id_counter, path.get_pretty_path())

                # Ensure vehicle can be spawned without collisions
                if not any(vehicle.collides_with(v) for v in vehicles):
                    self.assign_id(vehicle)
                    vehicle.after_create()
                    vehicles.append(vehicle)

                # Schedule next spawn
                delay = random.expovariate(vpm / 60) * 5000
                self.next_spawn_times[key] = current_time + delay

        # Spawn a bus if it's time
        if self.car_routes and current_time >= getattr(self, 'next_bus_spawn_time', 0):
            if self.spawn_priority_vehicle(vehicles, "bus"):
                self.next_bus_spawn_time = current_time + self.get_random_bus_delay()
            else:
                # Retry sooner if spawn failed due to collision
                self.next_bus_spawn_time = current_time + 5000

        # Spawn an emergency vehicle if it's time
        if self.car_routes and current_time >= getattr(self, 'next_emergency_spawn_time', 0):
            if self.spawn_priority_vehicle(vehicles, "emergency_vehicle"):
                self.next_emergency_spawn_time = current_time + self.get_random_emergency_delay()
            else:
                # Retry sooner if spawn failed due to collision
                self.next_emergency_spawn_time = current_time + 5000
