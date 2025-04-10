from lib.vehicles.vehicle import Vehicle

class Pedestrian(Vehicle):
    sprite_width = 6
    sprite_height = 6
    image_folder = "pedestrians"
    speed = 1

    def __init__(self, path):
        super().__init__(path, self.speed, self.sprite_width, self.sprite_height, self.image_folder)