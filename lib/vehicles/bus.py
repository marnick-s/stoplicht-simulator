from lib.vehicles.vehicle import Vehicle

class Bus(Vehicle):
    sprite_width = 22
    sprite_height = 10
    vehicle_type_string = "bus"
    speed = 60

    def __init__(self, id, path):
        super().__init__(id, path, self.speed, self.sprite_width, self.sprite_height, self.vehicle_type_string)