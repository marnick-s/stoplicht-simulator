from lib.vehicles.vehicle import Vehicle

class Car(Vehicle):
    sprite_width = 22
    sprite_height = 10
    vehicle_type_string = "car"
    speed = 60

    def __init__(self, path):
        super().__init__(path, self.speed, self.sprite_width, self.sprite_height, self.vehicle_type_string)