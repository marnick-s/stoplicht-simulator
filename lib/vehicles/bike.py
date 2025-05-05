from lib.vehicles.supports_collision_free_zones import SupportsCollisionFreeZones
from lib.vehicles.vehicle import Vehicle

class Bike(Vehicle, SupportsCollisionFreeZones):
    vehicle_type_string = "bike"
    speed = 60

    def __init__(self, id, path):
        Vehicle.__init__(self, id, path, self.speed, self.vehicle_type_string)
        SupportsCollisionFreeZones.__init__(self, self.x, self.y)