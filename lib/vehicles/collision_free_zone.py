from lib.collidable_object import CollidableObject, Hitbox
from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class CollisionFreeZone(CollidableObject):
    """
    Represents a rectangular collision-free zone defined by exactly four points.
    Used to mark areas where no collisions should occur.
    """
    def __init__(self, zone_dict: dict):
        """
        Initialize zone from dictionary with 'id' and 'zone' points.
        
        :param zone_dict: Dictionary containing 'id' and 'zone' (list of four (x,y) points).
        :raises ValueError: if zone does not have exactly 4 points.
        """
        self.id = zone_dict["id"]

        points = zone_dict.get("zone", [])
        if len(points) != 4:
            raise ValueError(f"Zone {self.id} moet exact 4 punten bevatten")

        xs = [pt[0] for pt in points]
        ys = [pt[1] for pt in points]

        x_min, y_min = min(xs), min(ys)
        x_max, y_max = max(xs), max(ys)

        self.position = Coordinate(x_min, y_min)
        self.width = x_max - x_min
        self.height = y_max - y_min

        self._cached_hitboxes = None

    def hitboxes(self):
        """
        Returns the rectangular hitbox of the zone, caching it for performance.
        """
        if self._cached_hitboxes is None:
            self._cached_hitboxes = [Hitbox(
                x=self.position.x,
                y=self.position.y,
                width=self.width,
                height=self.height
            )]
        return self._cached_hitboxes

    def draw(self):
        """
        Draw the collision-free zone on screen if width == 5.
        Scales coordinates and dimensions for display.
        """
        if (self.width == 5):
            x, y = scale_to_display(self.position.x, self.position.y)
            width, height = scale_to_display(self.width, self.height)
            screen.fill(self.color, (
                x,
                y,
                width,
                height
            ))
