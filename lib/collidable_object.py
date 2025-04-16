from abc import ABC, abstractmethod

class CollidableObject(ABC):
    @abstractmethod
    def hitboxes(self):
        """Object needs to have one or multiple hitboxes."""
        exit

    def can_collide(self, vehicle_direction=None):
        """Check if the object can collide with a vehicle. By default, all objects can collide."""
        return True
    
    def collides_with(self, obstacle, vehicle_direction=None, collision_angle=None, vehicle_type=None):
        if obstacle != self and obstacle.can_collide(vehicle_direction=vehicle_direction, vehicle_type=vehicle_type):
            # Alleen voorkant checken als collision_angle gegeven is
            hitboxes_to_check = [self.hitboxes()[-1]] if collision_angle is not None else self.hitboxes()
            # hitboxes_to_check = self.hitboxes()

            # Als er een angle check is, controleer of de hoek van het voertuig overeenkomt
            if collision_angle is not None:
                angle_diff = (self.angle - collision_angle + 180) % 360 - 180
                if abs(angle_diff) > 0:  # marge van ±30°
                    return False  # Niet in de juiste richting

            for hitbox in hitboxes_to_check:
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