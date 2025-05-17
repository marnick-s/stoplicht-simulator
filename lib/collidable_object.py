from abc import ABC, abstractmethod
from numba import njit

class Hitbox:
    """
    Axis-aligned bounding box (AABB).
    """
    __slots__ = ("x", "y", "width", "height")

    def __init__(self, x: float, y: float, width: float, height: float):
        # Initialize the hitbox with position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def collides_with(self, other: "Hitbox") -> bool:
        """
        Narrow-phase AABB-vs-AABB check.
        """
        # Use the optimized static method to check for collision
        return Hitbox.aabb_collide(
            self.x, self.y, self.width, self.height,
            other.x, other.y, other.width, other.height
        )

    @njit
    def aabb_collide(x1, y1, w1, h1, x2, y2, w2, h2):
        # Optimized AABB collision check using Numba for performance
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)

    def combine(self, b: "Hitbox") -> "Hitbox":
        """
        Return the minimal AABB enclosing both a and b.
        """
        # Compute the bounding box that encompasses both hitboxes
        min_x = min(self.x, b.x)
        min_y = min(self.y, b.y)
        max_x = max(self.x + self.width, b.x + b.width)
        max_y = max(self.y + self.height, b.y + b.height)
        return Hitbox(min_x, min_y, max_x - min_x, max_y - min_y)


class CollidableObject(ABC):
    """
    Base class for an object with one or more hitboxes.
    """

    @abstractmethod
    def hitboxes(self) -> list[Hitbox]:
        """
        Must return a list of Hitbox instances.
        """
        ...

    def can_collide(self,
                    vehicle_direction: float = None,
                    vehicle_type: str = None) -> bool:
        """
        By default, all objects can collide. Override this for exceptions.
        """
        return True

    def collides_with(self,
                      obstacle: "CollidableObject",
                      *,
                      vehicle_direction: float = None,
                      collision_angle: float = None,
                      vehicle_type: str = None,
                      angle_margin: float = 30.0) -> bool:
        """
        Broad-phase + narrow-phase collision detection, with optional directional filtering.
        """
        # 1) Quick rejection: skip self-collision and check if the object can be collided with
        if obstacle is self or not obstacle.can_collide(vehicle_direction, vehicle_type):
            return False

        # 2) Cache hitboxes once
        my_boxes = self.hitboxes()
        obs_boxes = obstacle.hitboxes()

        # 3) Broad-phase check: use overall AABB to quickly eliminate most non-collisions
        if not self._broad_phase_check(my_boxes, obs_boxes):
            return False

        # 4) Optional directional check and front-only hitbox selection
        if collision_angle is not None:
            # Use only the front-facing hitbox (assumed to be the last one)
            my_boxes = [my_boxes[-1]]

            angle_diff = (self.angle - collision_angle + 180) % 360 - 180
            if abs(angle_diff) > angle_margin:
                return False

        # 5) Narrow-phase check: actual hitbox-vs-hitbox collision testing
        for hb in my_boxes:
            for ob in obs_boxes:
                if hb.collides_with(ob):
                    return True

        return False

    @staticmethod
    def _broad_phase_check(boxes1: list[Hitbox], boxes2: list[Hitbox]) -> bool:
        """
        Compute the AABB of each list and test those first.
        """
        # Combine all hitboxes in each group to a single bounding box
        a = boxes1[0]
        for hb in boxes1[1:]:
            a = a.combine(hb)

        b = boxes2[0]
        for hb in boxes2[1:]:
            b = b.combine(hb)

        # Check if the resulting bounding boxes overlap
        return a.collides_with(b)
