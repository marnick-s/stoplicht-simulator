from lib.vehicles.vehicle import Vehicle

class Boat(Vehicle):
    sprite_width = 36
    sprite_height = 20
    vehicle_type_string = "boat"
    speed = 1

    def __init__(self, path):
        super().__init__(path, self.speed, self.sprite_width, self.sprite_height, self.vehicle_type_string)