from lib.vehicles.vehicle import Vehicle

class Boat(Vehicle):
    vehicle_type_string = "boat"
    speed = 10

    def __init__(self, id, path):
        super().__init__(id, path, self.speed, self.vehicle_type_string)