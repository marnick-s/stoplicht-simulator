from abc import ABC, abstractmethod

class CollidableObject(ABC):
    @abstractmethod
    def hitboxes(self):
        """Object needs to have one or multiple hitboxes."""
        exit

    def can_collide(self):
        return True
    
    def collides_with(self, obstacle):
        if obstacle != self and obstacle.can_collide():
            for hitbox in self.hitboxes():
                for obstacle_hitbox in obstacle.hitboxes():
                    if hitbox.collides_with(obstacle_hitbox):
                        return True
        return False

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