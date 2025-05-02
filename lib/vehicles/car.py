from lib.vehicles.vehicle import Vehicle

class Car(Vehicle):
    vehicle_type_string = "car"
    speed = 60

    def __init__(self, id, path):
        super().__init__(id, path, self.speed, self.vehicle_type_string)