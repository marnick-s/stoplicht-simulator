from lib.basic_traffic_manager import BasicTrafficManager
from lib.bridge.bridge import Bridge
from lib.directions.direction import Direction
from lib.directions.sensor import Sensor
from lib.enums.topics import Topics
from lib.vehicles.vehicle import Vehicle
from lib.vehicles.vehicle_spawner import VehicleSpawner

class Simulation:
    def __init__(self, config, messenger, traffic_level="rustig"):
        self.vehicles = []
        self.config = config
        self.messenger = messenger
        self.basic_traffic_manager = BasicTrafficManager()
        self.directions = self.load_directions(config)
        self.vehicle_spawner = VehicleSpawner(config, traffic_level)
        self.previous_lane_sensor_data = {}
        self.previous_special_sensor_data = {}
        self.collision_free_zones = config.get("collision_free_zones", [])
        Vehicle.collision_free_zones = self.collision_free_zones # Set collision free zones for all vehicles
        self.bridge = Bridge(messenger)
        self.load_special_sensors()


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
        self.vehicle_spawner.create_new_vehicles(self.vehicles)
        self.update_traffic_lights()
        self.bridge.update()
        self.vehicles[:] = [v for v in self.vehicles if not v.has_finished()] # Remove finished vehicles
        obstacles = self.vehicles + [light for d in self.directions for light in d.traffic_lights]
        for vehicle in self.vehicles:
            vehicle.move(obstacles)
        self.check_occupied_sensors()


    def update_traffic_lights(self):
        if self.messenger.connected:
            traffic_light_data = self.messenger.traffic_light_data
        else:
            traffic_light_data = self.basic_traffic_manager.traffic_light_data

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

        for name, sensor in self.special_sensors.items():
            specialSensorData[name] = False
        for direction in self.directions:
            for traffic_light in direction.traffic_lights:
                sensor_id = f"{direction.id}.{traffic_light.id}"
                laneSensorData[sensor_id] = {"voor": False, "achter": False}

        for vehicle in self.vehicles:
            for name, sensor in self.special_sensors.items():
                if vehicle.collides_with(sensor, vehicle_type=vehicle.vehicle_type_string):
                    specialSensorData[name] = True

            for direction in self.directions:
                for traffic_light in direction.traffic_lights:
                    sensor_id = f"{direction.id}.{traffic_light.id}"
                    if vehicle.collides_with(traffic_light.front_sensor):
                        laneSensorData[sensor_id]["achter"] = True
                    if traffic_light.back_sensor and vehicle.collides_with(traffic_light.back_sensor):
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