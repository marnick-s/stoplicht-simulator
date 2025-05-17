from lib.collidable_object import CollidableObject, Hitbox
from lib.screen import screen, scale_to_display
from lib.coordinate import Coordinate

class Sensor(CollidableObject):
    """
    Represents a sensor in the simulation that can detect vehicle collisions.
    Can be configured to only detect specific vehicle types or directions.
    """

    def __init__(self, position, dimensions=(5, 5), approach_direction=None, vehicle_types=[]):
        """
        Initialize the Sensor with its position, size, and optional filtering rules.

        Args:
            position (tuple): (x, y) coordinates of the sensor.
            dimensions (tuple): (width, height) of the sensor hitbox.
            approach_direction (str, optional): Direction from which vehicles can trigger the sensor.
            vehicle_types (list, optional): List of vehicle types this sensor can detect.
        """
        self.position = Coordinate(*position)
        self.width, self.height = dimensions
        self.color = (0, 0, 255)
        self.approach_direction = approach_direction
        self.vehicle_types = vehicle_types
        self._cached_hitboxes = None

    def can_collide(self, vehicle_direction=None, vehicle_type=None):
        """
        Check if a vehicle can interact with this sensor.

        Args:
            vehicle_direction (str, optional): The direction the vehicle is approaching from.
            vehicle_type (str, optional): Type of the vehicle.

        Returns:
            bool: True if the vehicle matches the sensor's filters, False otherwise.
        """
        if vehicle_direction and vehicle_direction != self.approach_direction:
            return False
        if vehicle_type and vehicle_type not in self.vehicle_types:
            return False
        return True

    def hitboxes(self):
        """
        Return the list of hitboxes representing this sensor's area.

        Returns:
            list[Hitbox]: List containing a single Hitbox.
        """
        if self._cached_hitboxes is None:
            # Calculate hitbox once and cache it
            half_width = self.width / 2
            half_height = self.height / 2
            self._cached_hitboxes = [Hitbox(
                x=self.position.x - half_width,
                y=self.position.y - half_height,
                width=self.width,
                height=self.height
            )]
        return self._cached_hitboxes

    def draw(self):
        """
        Optional debug drawing for visualizing the sensor on screen.
        Currently disabled.
        """
        pass
        # if self.width == 5:
        #     x, y = scale_to_display(self.position.x, self.position.y)
        #     width, height = scale_to_display(self.width, self.height)
        #     screen.fill(self.color, (
        #         x - width // 2,
        #         y - height // 2,
        #         width,
        #         height
        #     ))
