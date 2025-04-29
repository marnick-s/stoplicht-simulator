from lib.bridge.bridge import Bridge
from lib.collidable_object import Hitbox
from lib.directions.direction import Direction
from lib.directions.sensor import Sensor
from lib.enums.topics import Topics
from lib.screen import WORLD_HEIGHT, WORLD_WIDTH
from lib.spatial.spatial_hash_grid import SpatialHashGrid
from lib.vehicles.vehicle import Vehicle
from lib.vehicles.vehicle_spawner import VehicleSpawner
import time

class Simulation:
    def __init__(self, config, messenger, traffic_level="rustig"):
        self.vehicles = []
        self.config = config
        self.messenger = messenger
        self.directions = self.load_directions(config)
        self.vehicle_spawner = VehicleSpawner(config, traffic_level)
        self.previous_lane_sensor_data = {}
        self.previous_special_sensor_data = {}
        self.collision_free_zones = config.get("collision_free_zones", [])
        Vehicle.collision_free_zones = self.collision_free_zones  # Set collision free zones for all vehicles
        self.bridge = Bridge(messenger)
        self.load_special_sensors()
        
        self.spatial_hash = SpatialHashGrid()  # Adjust cell size based on your world
        
        # Time-based movement tracking
        self.last_update_time = time.time()

    def load_directions(self, config):
        directions = []
        for direction_type, direction_list in config['directions'].items():
            for direction_data in direction_list:
                direction_data['type'] = direction_type
                directions.append(Direction(direction_data))
        return directions
    
    def load_special_sensors(self):
        self.special_sensors = {
            sensor["name"]: Sensor(
                position=sensor.get("position"),
                dimensions=sensor.get("dimensions"),
                vehicle_types=sensor.get("vehicle_types", []),
            )
            for sensor in self.config.get("special_sensors", [])
        }


    def update(self):
        # Calculate time delta for time-based movement
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        # Init spatial hash grid
        self.spatial_hash.clear()
        
        # Add all collidable objects to the spatial hash
        collidables = []
        collidables.extend(self.vehicles)
        for direction in self.directions:
            collidables.extend(direction.traffic_lights)
        
        for obj in collidables:
            self.spatial_hash.insert(obj)
        
        # Process vehicle movements
        vehicle_movements = {}
        for vehicle in self.vehicles:
            # Create a query region around the vehicle
            buffer = 20  # Buffer size in pixels
            vehicle_hitboxes = vehicle.hitboxes()
            min_x = min(hb.x for hb in vehicle_hitboxes) - buffer
            max_x = max(hb.x + hb.width for hb in vehicle_hitboxes) + buffer
            min_y = min(hb.y for hb in vehicle_hitboxes) - buffer
            max_y = max(hb.y + hb.height for hb in vehicle_hitboxes) + buffer
            query_box = Hitbox(min_x, min_y, max_x - min_x, max_y - min_y)
            
            # Query spatial hash for obstacle candidates
            obstacle_candidates = self.spatial_hash.query(query_box)
            obstacles = [obj for obj in obstacle_candidates if obj is not vehicle]
            
            # Calculate next position
            movement_data = vehicle.calculate_next_position(obstacles)
            vehicle_movements[vehicle] = movement_data
            
        # Apply all movements after all calculations are done
        for vehicle, movement_data in vehicle_movements.items():
            vehicle.apply_movement(movement_data)

        # Other updates
        self.vehicle_spawner.create_new_vehicles(self.vehicles)
        self.update_traffic_lights()
        self.bridge.update(delta_time)
        self.vehicles[:] = [v for v in self.vehicles if not v.has_finished()]
        self.check_occupied_sensors()


    def update_traffic_lights(self):
        traffic_light_data = self.messenger.traffic_light_data

        if not traffic_light_data:
            return
        if "81.1" in traffic_light_data:
            self.bridge.update_state(traffic_light_data["81.1"], traffic_light_data["41.1"])
        for direction in self.directions:
            for traffic_light in direction.traffic_lights:
                sensor_id = f"{direction.id}.{traffic_light.id}"
                if sensor_id in traffic_light_data:
                    new_color = traffic_light_data[sensor_id]
                    traffic_light.update(new_color)
    

    def check_occupied_sensors(self):
        laneSensorData = {}
        specialSensorData = {}

        # Initialize sensor data
        for name, sensor in self.special_sensors.items():
            specialSensorData[name] = False
        for direction in self.directions:
            for traffic_light in direction.traffic_lights:
                sensor_id = f"{direction.id}.{traffic_light.id}"
                laneSensorData[sensor_id] = {"voor": False, "achter": False}

        # Create a temporary spatial hash grid for sensors
        sensor_grid = SpatialHashGrid()
        
        # Add all sensors to the grid
        for name, sensor in self.special_sensors.items():
            sensor_grid.insert(sensor)
        
        for direction in self.directions:
            for traffic_light in direction.traffic_lights:
                if traffic_light.front_sensor:
                    sensor_grid.insert(traffic_light.front_sensor)
                if traffic_light.back_sensor:
                    sensor_grid.insert(traffic_light.back_sensor)

        # Check each vehicle against nearby sensors only
        for vehicle in self.vehicles:
            vehicle_hitboxes = vehicle.hitboxes()
            buffer = 5  # Smaller buffer for sensors is sufficient
            min_x = min(hb.x for hb in vehicle_hitboxes) - buffer
            max_x = max(hb.x + hb.width for hb in vehicle_hitboxes) + buffer
            min_y = min(hb.y for hb in vehicle_hitboxes) - buffer
            max_y = max(hb.y + hb.height for hb in vehicle_hitboxes) + buffer
            query_box = Hitbox(min_x, min_y, max_x - min_x, max_y - min_y)
            
            # Query only for nearby sensors
            nearby_sensors = sensor_grid.query(query_box)
            
            # Check collisions with special sensors
            for sensor_obj in nearby_sensors:
                # Check special sensors
                for name, sensor in self.special_sensors.items():
                    if sensor_obj is sensor and vehicle.collides_with(sensor, vehicle_type=vehicle.vehicle_type_string):
                        specialSensorData[name] = True
                
                # Check traffic light sensors
                for direction in self.directions:
                    for traffic_light in direction.traffic_lights:
                        sensor_id = f"{direction.id}.{traffic_light.id}"
                        if sensor_obj is traffic_light.front_sensor and vehicle.collides_with(traffic_light.front_sensor):
                            laneSensorData[sensor_id]["achter"] = True
                        if traffic_light.back_sensor and sensor_obj is traffic_light.back_sensor and vehicle.collides_with(traffic_light.back_sensor):
                            laneSensorData[sensor_id]["voor"] = True

        if (laneSensorData != self.previous_lane_sensor_data):
            self.previous_lane_sensor_data = laneSensorData
            self.messenger.send(Topics.LANE_SENSORS_UPDATE.value, laneSensorData)

        if (specialSensorData != self.previous_special_sensor_data):
            self.previous_special_sensor_data = specialSensorData
            self.messenger.send(Topics.SPECIAL_SENSORS_UPDATE.value, specialSensorData)

    def draw(self):
        self.bridge.draw()
        for vehicle in self.vehicles:
            vehicle.draw()
        for direction in self.directions:
            direction.draw(self.messenger.connected)
        for name, sensor in self.special_sensors.items():
            sensor.draw()
        
        # Debug visualization for spatial partitioning
        self.spatial_hash.draw()