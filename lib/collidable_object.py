from abc import ABC, abstractmethod

class CollidableObject(ABC):
    @abstractmethod
    def hitbox(self):
        """Object needs to have a hitbox."""
        pass

    def can_collide(self):
        return True

class Hitbox:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def collides_with(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)