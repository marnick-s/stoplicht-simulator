from lib.collidable_object import CollidableObject, Hitbox
from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class Sensor(CollidableObject):
    def __init__(self, position, dimensions=(5, 5), approach_direction=None, vehicle_types=[]):
        self.position = Coordinate(*position)
        self.width, self.height = dimensions
        self.color = (0, 0, 255)
        self.approach_direction = approach_direction
        self.vehicle_types = vehicle_types

    def can_collide(self, vehicle_direction=None, vehicle_type=None):
        if vehicle_direction and vehicle_direction != self.approach_direction:
            return False
        if vehicle_type and vehicle_type not in self.vehicle_types:
            return False
        return True

    def hitboxes(self):
        half_width = self.width / 2
        half_height = self.height / 2
        return [Hitbox(
            x=self.position.x - half_width,
            y=self.position.y - half_height,
            width=self.width,
            height=self.height
        )]

    def draw(self):
        x, y = scale_to_display(self.position.x, self.position.y)
        width, height = scale_to_display(self.width, self.height)
        screen.fill(self.color, (
            x - width // 2,
            y - height // 2,
            width,
            height
        ))
