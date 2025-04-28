from lib.vehicles.supports_collision_free_zones import SupportsCollisionFreeZones
from lib.vehicles.vehicle import Vehicle

class Pedestrian(Vehicle, SupportsCollisionFreeZones):
    sprite_width = 6
    sprite_height = 6
    vehicle_type_string = "pedestrian"
    speed = 10

    def __init__(self, path):
        Vehicle.__init__(self, path, self.speed, self.sprite_width, self.sprite_height, self.vehicle_type_string)
        SupportsCollisionFreeZones.__init__(self, self.x, self.y)