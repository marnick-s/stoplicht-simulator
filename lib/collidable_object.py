from abc import ABC, abstractmethod
from numba import njit

class Hitbox:
    """
    Axis-aligned bounding box (AABB).
    """
    __slots__ = ("x", "y", "width", "height")

    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def collides_with(self, other: "Hitbox") -> bool:
        """
        Narrow-phase AABB-vs-AABB check.
        """
        return Hitbox.aabb_collide(self.x, self.y, self.width, self.height, other.x, other.y, other.width, other.height)
        # return (
        #     self.x < other.x + other.width and
        #     self.x + self.width > other.x and
        #     self.y < other.y + other.height and
        #     self.y + self.height > other.y
        # )
    
    @njit
    def aabb_collide(x1, y1, w1, h1, x2, y2, w2, h2):
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)

    def combine(self, b: "Hitbox") -> "Hitbox":
        """
        Return the minimal AABB enclosing both a en b.
        """
        min_x = min(self.x, b.x)
        min_y = min(self.y, b.y)
        max_x = max(self.x + self.width, b.x + b.width)
        max_y = max(self.y + self.height, b.y + b.height)
        return Hitbox(min_x, min_y, max_x - min_x, max_y - min_y)


class CollidableObject(ABC):
    """
    Basis voor een object met één of meerdere hitboxes.
    """

    @abstractmethod
    def hitboxes(self) -> list[Hitbox]:
        """
        Moet een lijst van Hitbox-instanties teruggeven.
        """
        ...

    def can_collide(self,
                    vehicle_direction: float = None,
                    vehicle_type: str = None) -> bool:
        """
        Standaard: alle objecten kunnen botsten. Overschrijf voor uitzonderingen.
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
        Broad-phase + narrow-phase collision detection, met optionele richtingcheck.
        """
        # 1) Snelafwijzing: niet met zichzelf en alleen met collidabele objecten
        if obstacle is self or not obstacle.can_collide(vehicle_direction, vehicle_type):
            return False

        # 2) Cache hitboxes éénmalig
        my_boxes = self.hitboxes()
        obs_boxes = obstacle.hitboxes()

        # 3) Broad-phase: gebruik één overkoepelende AABB om de meeste checks te skippen
        if not self._broad_phase_check(my_boxes, obs_boxes):
            return False

        # 4) Optionele hoekverificatie & voorkant-selectie
        if collision_angle is not None:
            # selecteer alleen de voorkant-hitbox (laatste in de lijst)
            my_boxes = [my_boxes[-1]]

            angle_diff = (self.angle - collision_angle + 180) % 360 - 180
            if abs(angle_diff) > angle_margin:
                return False

        # 5) Narrow-phase: échte hitbox-vs-hitbox checks
        for hb in my_boxes:
            for ob in obs_boxes:
                if hb.collides_with(ob):
                    return True

        return False

    @staticmethod
    def _broad_phase_check(boxes1: list[Hitbox], boxes2: list[Hitbox]) -> bool:
        """
        Bereken de AABB van iedere lijst en test die eerst.
        """
        # start met de eerste
        a = boxes1[0]
        for hb in boxes1[1:]:
            a = a.combine(hb)

        b = boxes2[0]
        for hb in boxes2[1:]:
            b = b.combine(hb)

        return a.collides_with(b)
