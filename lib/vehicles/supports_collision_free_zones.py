from abc import ABC

class SupportsCollisionFreeZones(ABC):
    """
    Mixin class for objects that can interact with defined collision-free zones.
    """
    collision_free_zones = []

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.exiting = None  # ID of the zone being exited, or None

    def in_same_cf_zone(self, obstacle):
        """
        Determines if this object and another are currently in the same collision-free zone.
        """
        return (
            self.is_in_zone() and 
            obstacle.is_in_zone() and 
            self.get_current_zone_id() == obstacle.get_current_zone_id()
        )

    def is_in_zone(self, target_zone_id=None) -> bool:
        """
        Check if the object is currently inside a defined collision-free zone.

        :param target_zone_id: Optional specific zone ID to check against.
        :return: True if inside a zone (or the specified one), False otherwise.
        """
        for zone in self.collision_free_zones:
            if target_zone_id is not None and zone.id == target_zone_id:
                return self.collides_with(zone)
            if self.collides_with(zone):
                return True
        return False

    def get_current_zone(self) -> dict:
        """
        Returns the zone object the entity is currently in.
        If it's not in any zone, an empty dictionary is returned.
        """
        for zone in self.collision_free_zones:
            if self.collides_with(zone):
                return zone
        return {}

    def get_current_zone_id(self) -> int:
        """
        Returns the ID of the zone the entity is currently in.
        If not in any zone, returns None.
        """
        for zone in self.collision_free_zones:
            if self.collides_with(zone):
                return zone.id
        return None

    def check_other_vehicles_exiting_zone(self, other_vehicles: list, zone_id: int) -> bool:
        """
        Ensures that only one vehicle can be in the process of exiting a zone at any given time.

        :param other_vehicles: List of all vehicles to check.
        :param zone_id: The ID of the zone in question.
        :return: True if another vehicle is exiting or obstructing the exit.
        """
        for v in other_vehicles:
            if v is not self and isinstance(v, SupportsCollisionFreeZones):
                if (v.is_exiting_zone() and v.exiting == zone_id) or \
                   (not v.is_in_zone() and self.collides_with(v)):
                    return True
        return False

    def can_exit_zone(self, other_vehicles: list, new_x: int, new_y: int, zone_id: int) -> bool:
        """
        Checks whether this vehicle can safely exit its current collision-free zone.

        :param other_vehicles: List of other vehicles to consider.
        :param new_x: Proposed new x-coordinate.
        :param new_y: Proposed new y-coordinate.
        :param zone_id: ID of the zone being exited.
        :return: True if exit is permitted, otherwise False.
        """
        # Temporarily move vehicle
        temp_x, temp_y = self.x, self.y
        self.x, self.y = new_x, new_y

        can_exit_zone = not self.check_other_vehicles_exiting_zone(other_vehicles, zone_id)

        # Restore position
        self.x, self.y = temp_x, temp_y
        return can_exit_zone

    def is_exiting_zone(self) -> bool:
        """
        Checks if the object is currently in 'exiting' mode (i.e., in the process of leaving a zone).

        :return: True if exiting, False otherwise.
        """
        return self.exiting is not None

    def release_exiting_if_possible(self, obstacles) -> bool:
        """
        Determines whether the object can stop being in 'exiting' mode.
        It must have left the zone and be free of collisions with other obstacles.

        :param obstacles: A list of objects to check collisions against.
        :return: True if exiting was released, False otherwise.
        """
        if self.is_exiting_zone() and not self.is_in_zone(self.exiting):
            has_collisions = any(self.collides_with(obstacle) for obstacle in obstacles)
            if not has_collisions:
                self.exiting = None
