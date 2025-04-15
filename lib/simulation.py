from lib.basic_traffic_manager import BasicTrafficManager
from lib.bridge import Bridge
from lib.directions.direction import Direction
from lib.enums.topics import Topics
from lib.vehicles.vehicle import Vehicle
from lib.vehicles.vehicle_spawner import VehicleSpawner

class Simulation:
    def __init__(self, config, messenger):
        self.vehicles = []
        self.config = config
        self.messenger = messenger
        self.basic_traffic_manager = BasicTrafficManager()
        self.directions = self.load_directions(config)
        self.vehicle_spawner = VehicleSpawner(config)
        self.previous_lane_sensor_data = {}
        self.previous_special_sensor_data = {}
        self.collision_free_zones = config.get("collision_free_zones", [])
        Vehicle.collision_free_zones = self.collision_free_zones # Set collision free zones for all vehicles
        self.bridge = Bridge()

    def load_directions(self, config):
        directions = []
        for direction_type, direction_list in config['directions'].items():
            for direction_data in direction_list:
                direction_data['type'] = direction_type
                directions.append(Direction(direction_data))
        return directions


    def update(self):
        self.bridge.update()
        self.vehicle_spawner.create_new_vehicles(self.vehicles)
        self.update_traffic_lights()
        self.vehicles[:] = [v for v in self.vehicles if not v.has_finished()] # Remove finished vehicles
        obstacles = self.vehicles + [light for d in self.directions for light in d.traffic_lights]
        for vehicle in self.vehicles:
            vehicle.move(obstacles)
        self.check_occupied_lane_sensors()


    def update_traffic_lights(self):
        if self.messenger.connected:
            traffic_light_data = self.messenger.traffic_light_data
        else:
            traffic_light_data = self.basic_traffic_manager.traffic_light_data

        if not traffic_light_data:
            return 
        for direction in self.directions:
            for traffic_light in direction.traffic_lights:
                sensor_id = f"{direction.id}.{traffic_light.id}"
                if sensor_id in traffic_light_data:
                    new_color = traffic_light_data[sensor_id]
                    traffic_light.update(new_color)


    def check_occupied_lane_sensors(self):
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

        if (sensorData != self.previous_lane_sensor_data):
            self.previous_lane_sensor_data = sensorData
            self.messenger.send(Topics.LANE_SENSORS_UPDATE.value, sensorData)


    def draw(self):
        self.bridge.draw()
        for vehicle in self.vehicles:
            vehicle.draw()
        for direction in self.directions:
            direction.draw(self.messenger.connected)