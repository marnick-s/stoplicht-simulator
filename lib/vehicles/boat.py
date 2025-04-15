from lib.vehicles.vehicle import Vehicle

class Boat(Vehicle):
    sprite_width = 36
    sprite_height = 20
    image_folder = "boats"
    speed = 1

    def __init__(self, path):
        super().__init__(path, self.speed, self.sprite_width, self.sprite_height, self.image_folder)