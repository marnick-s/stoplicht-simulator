from lib.vehicles.vehicle import Vehicle

class Bus(Vehicle):
    vehicle_type_string = "bus"
    speed = 60

    def __init__(self, id, path):
        super().__init__(id, path, self.speed, self.vehicle_type_string)