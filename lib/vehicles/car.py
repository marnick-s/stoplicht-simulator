from lib.vehicles.vehicle import Vehicle

class Car(Vehicle):
    sprite_width = 28
    sprite_height = 14
    image_folder = "cars"
    speed = 2

    def __init__(self, path):
        super().__init__(path, self.speed, self.sprite_width, self.sprite_height, self.image_folder)