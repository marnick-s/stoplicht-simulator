from lib.collidable_object import CollidableObject, Hitbox
from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class Sensor(CollidableObject):
    def __init__(self, position, approach_direction=None):
        self.position = Coordinate(*position)
        self.color = (0, 0, 255)
        self.size = 5
        self.approach_direction = approach_direction

    def can_collide(self, vehicle_direction):
        if vehicle_direction != self.approach_direction:
            return False
        return True

    def hitboxes(self):
        half_size = self.size / 2
        return [Hitbox(
            x=self.position.x - half_size,
            y=self.position.y - half_size,
            width=self.size,
            height=self.size
        )]

    def draw(self):
        x, y = scale_to_display(self.position.x, self.position.y)
        width, height = scale_to_display(self.size, self.size)
        screen.fill(self.color, (
            x - width // 2,
            y - height // 2,
            width,
            height
        ))
