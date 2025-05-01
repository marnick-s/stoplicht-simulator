from lib.vehicles.supports_collision_free_zones import SupportsCollisionFreeZones
from lib.vehicles.vehicle import Vehicle

class Pedestrian(Vehicle, SupportsCollisionFreeZones):
    sprite_width = 4
    sprite_height = 4
    vehicle_type_string = "pedestrian"
    speed = 10

    def __init__(self, id, path):
        Vehicle.__init__(self, id, path, self.speed, self.sprite_width, self.sprite_height, self.vehicle_type_string)
        SupportsCollisionFreeZones.__init__(self, self.x, self.y)