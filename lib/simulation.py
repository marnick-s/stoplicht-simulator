import pygame
from lib.bridge.bridge import Bridge
from lib.collidable_object import Hitbox
from lib.directions.direction import Direction
from lib.directions.sensor import Sensor
from lib.enums.topics import Topics
from lib.spatial.spatial_hash_grid import SpatialHashGrid
from lib.vehicles.collision_free_zone import CollisionFreeZone
from lib.vehicles.vehicle import Vehicle
from lib.vehicles.vehicle_spawner import VehicleSpawner
import time
from pygame import mixer

class Simulation:
    def __init__(self, config, messenger, traffic_level="rustig"):
        self.vehicles = []
        self.config = config
        self.traffic_level = traffic_level
        self.messenger = messenger
        self.directions = self.load_directions(config)
        self.vehicle_spawner = VehicleSpawner(config, traffic_level, messenger)
        self.previous_lane_sensor_data = {}
        self.previous_special_sensor_data = {}
        self.collision_free_zones = config.get("collision_free_zones", [])
        
        # Set global collision free zones for all vehicles
        Vehicle.collision_free_zones = self.load_collision_free_zones_from_config()
        
        self.bridge = Bridge(messenger)
        self.load_special_sensors()
        self.play_noise()
        
        # Initialize spatial partitioning system with larger cell size for fewer buckets
        self.spatial_hash = SpatialHashGrid(cell_size=60)
        
        # Create a separate grid for sensors which don't move often
        self.sensor_grid = SpatialHashGrid(cell_size=80)
        self.initialize_sensor_grid()
        
        # Track simulation time
        self.last_update_time = time.time()
        
        # Reusable objects to avoid recreating them each frame
        self.query_buffer = 25  # Buffer for spatial queries
        self.collidables = []
        
        # Keep track of active traffic lights to avoid recalculating
        self.active_traffic_lights = []
        self.update_active_traffic_lights()

    # Play background noise sound if audio is enabled
    def play_noise(self):
        if pygame.mixer.get_init():
            sound = mixer.Sound("assets/sounds/noise.mp3")
            sound.set_volume(0.5)
            sound.play(loops=-1, maxtime=0, fade_ms=0)

    # Parse collision-free zones from the configuration file
    def load_collision_free_zones_from_config(self) -> list[CollisionFreeZone]:
        zones = []
        for zone_dict in self.config.get("collision_free_zones", []):
            try:
                zones.append(CollisionFreeZone(zone_dict))
            except Exception as e:
                print(f"Error in zone {zone_dict.get('id', '?')}: {e}")
        return zones

    # Load all direction objects from the configuration
    def load_directions(self, config):
        directions = []
        bridge_closed = self.traffic_level == "spits"
        for direction_type, direction_list in config['directions'].items():
            for direction_data in direction_list:
                direction_data['type'] = direction_type
                directions.append(Direction(direction_data, bridge_closed))
        return directions
    
    # Load special sensors defined in the config
    def load_special_sensors(self):
        self.special_sensors = {
            sensor["name"]: Sensor(
                position=sensor.get("position"),
                dimensions=sensor.get("dimensions"),
                vehicle_types=sensor.get("vehicle_types", []),
            )
            for sensor in self.config.get("special_sensors", [])
        }
    
    # Initialize sensor grid once since sensors don't move
    def initialize_sensor_grid(self):
        # Add special sensors to grid
        for name, sensor in self.special_sensors.items():
            self.sensor_grid.insert(sensor)
        
        # Add traffic light sensors to grid
        for direction in self.directions:
            for traffic_light in direction.traffic_lights:
                if traffic_light.front_sensor:
                    self.sensor_grid.insert(traffic_light.front_sensor)
                if traffic_light.back_sensor:
                    self.sensor_grid.insert(traffic_light.back_sensor)
    
    # Update active traffic lights list
    def update_active_traffic_lights(self):
        self.active_traffic_lights = []
        for direction in self.directions:
            self.active_traffic_lights.extend(direction.traffic_lights)

    # Main simulation update method (called every frame)
    def update(self):
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        # Clear and repopulate spatial hash
        self.spatial_hash.clear()
        
        # Gather all collidable objects (vehicles + traffic lights)
        self.collidables.clear()
        self.collidables.extend(self.vehicles)
        self.collidables.extend(self.active_traffic_lights)
        
        # Insert all collidables into spatial hash in one pass
        for obj in self.collidables:
            self.spatial_hash.insert(obj)
        
        # Compute new positions for each vehicle
        vehicle_movements = {}
        for vehicle in self.vehicles:
            # Get vehicle's bounding box for spatial query
            vehicle_hitboxes = vehicle.hitboxes()
            min_x = min(hb.x for hb in vehicle_hitboxes) - self.query_buffer
            max_x = max(hb.x + hb.width for hb in vehicle_hitboxes) + self.query_buffer
            min_y = min(hb.y for hb in vehicle_hitboxes) - self.query_buffer
            max_y = max(hb.y + hb.height for hb in vehicle_hitboxes) + self.query_buffer
            query_box = Hitbox(min_x, min_y, max_x - min_x, max_y - min_y)
            
            # Get nearby objects to check for collisions (only use what's needed)
            obstacle_candidates = self.spatial_hash.query(query_box)
            obstacles = [obj for obj in obstacle_candidates if obj is not vehicle]
            
            # Let the vehicle compute its next move
            movement_data = vehicle.calculate_next_position(obstacles)
            vehicle_movements[vehicle] = movement_data
            
        # Apply calculated movements in batch
        for vehicle, movement_data in vehicle_movements.items():
            vehicle.apply_movement(movement_data)

        # Update other simulation elements
        self.vehicle_spawner.update(self.vehicles)
        self.update_traffic_lights()
        self.bridge.update(delta_time)
        
        # Remove vehicles that have completed their path using list comprehension
        self.vehicles = [v for v in self.vehicles if not v.has_finished()]

        # Check if any sensors are triggered
        self.check_occupied_sensors()

    # Update traffic lights based on received data
    def update_traffic_lights(self):
        traffic_light_data = self.messenger.traffic_light_data

        if not traffic_light_data:
            return
            
        if "81.1" in traffic_light_data and "41.1" in traffic_light_data:
            self.bridge.update_state(traffic_light_data["81.1"], traffic_light_data["41.1"])
            
        for direction in self.directions:
            for traffic_light in direction.traffic_lights:
                sensor_id = f"{direction.id}.{traffic_light.id}"
                if sensor_id in traffic_light_data:
                    new_color = traffic_light_data[sensor_id]
                    traffic_light.update(new_color)

    # Determine which sensors are occupied by vehicles with improved efficiency
    def check_occupied_sensors(self):
        # Define directions to skip
        directions_to_skip = [41, 42, 51, 52, 53, 54]
        
        # Initialize dictionaries with default values - excluding the directions to skip
        laneSensorData = {
            f"{direction.id}.{traffic_light.id}": {"voor": False, "achter": False}
            for direction in self.directions
            for traffic_light in direction.traffic_lights
            if direction.id not in directions_to_skip  # Skip specified directions
        }
    
        specialSensorData = {name: False for name in self.special_sensors}
        
        # Check vehicles for collisions with nearby sensors
        for vehicle in self.vehicles:
            # Get vehicle's bounding box for spatial query
            vehicle_hitboxes = vehicle.hitboxes()
        
            # Calculate query box around vehicle
            min_x = min(hb.x for hb in vehicle_hitboxes) - 5  # Small buffer
            max_x = max(hb.x + hb.width for hb in vehicle_hitboxes) + 5
            min_y = min(hb.y for hb in vehicle_hitboxes) - 5
            max_y = max(hb.y + hb.height for hb in vehicle_hitboxes) + 5
            query_box = Hitbox(min_x, min_y, max_x - min_x, max_y - min_y)
        
            # Query sensor grid for potential sensor collisions
            nearby_sensors = self.sensor_grid.query(query_box)
        
            # Test actual collisions
            for sensor_obj in nearby_sensors:
                # Special sensor check
                for name, sensor in self.special_sensors.items():
                    if sensor_obj is sensor and vehicle.collides_with(sensor, vehicle_type=vehicle.vehicle_type_string):
                        specialSensorData[name] = True
            
                # Lane sensor check (front and back) - skip specified directions
                for direction in self.directions:
                    # Skip processing for directions in our skip list
                    if direction.id in directions_to_skip:
                        continue
                        
                    for traffic_light in direction.traffic_lights:
                        sensor_id = f"{direction.id}.{traffic_light.id}"
                        if sensor_obj is traffic_light.front_sensor and vehicle.collides_with(traffic_light.front_sensor):
                            laneSensorData[sensor_id]["voor"] = True
                        if traffic_light.back_sensor and sensor_obj is traffic_light.back_sensor and vehicle.collides_with(traffic_light.back_sensor):
                            laneSensorData[sensor_id]["achter"] = True
        
        # Send updates only if data changed
        if laneSensorData != self.previous_lane_sensor_data:
            self.previous_lane_sensor_data = laneSensorData
            self.messenger.send(Topics.LANE_SENSORS_UPDATE.value, laneSensorData)
        if specialSensorData != self.previous_special_sensor_data:
            self.previous_special_sensor_data = specialSensorData
            self.messenger.send(Topics.SPECIAL_SENSORS_UPDATE.value, specialSensorData)

    # Draw all simulation elements to the screen
    def draw(self):
        self.bridge.draw()
        for vehicle in self.vehicles:
            vehicle.draw()
        for direction in self.directions:
            direction.draw(self.messenger.connected)
        for name, sensor in self.special_sensors.items():
            sensor.draw()
        
        # Uncomment to draw debug grid for spatial hashing
        # self.spatial_hash.draw(color=(150, 150, 150))