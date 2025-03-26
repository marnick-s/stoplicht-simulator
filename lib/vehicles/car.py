from lib.vehicles.vehicle import Vehicle

class Car(Vehicle):
    sprite_width = 44
    sprite_height = 24
    image_folder = "cars"

    def __init__(self, path, speed=2):
        super().__init__(path, speed, self.sprite_width, self.sprite_height, self.image_folder)