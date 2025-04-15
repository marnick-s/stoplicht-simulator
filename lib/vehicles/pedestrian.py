from lib.vehicles.supports_collision_free_zones import SupportsCollisionFreeZones
from lib.vehicles.vehicle import Vehicle

class Pedestrian(Vehicle, SupportsCollisionFreeZones):
    sprite_width = 6
    sprite_height = 6
    image_folder = "pedestrians"
    speed = 1

    def __init__(self, path):
        Vehicle.__init__(self, path, self.speed, self.sprite_width, self.sprite_height, self.image_folder)
        SupportsCollisionFreeZones.__init__(self, self.x, self.y)