from abc import ABC

class SupportsCollisionFreeZones(ABC):
    collision_free_zones = []  

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.exiting = None

    def in_same_cf_zone(self, obstacle):
        return self.is_in_zone() and obstacle.is_in_zone() and self.get_current_zone() == obstacle.get_current_zone()

    def is_in_zone(self, target_zone_id=None) -> bool:
        """
        Bepaalt of het voertuig zich in één van de gedefinieerde collision free zones bevindt.
        """
        for zone in self.collision_free_zones:
            if zone.id == target_zone_id:
                return self.collides_with(zone)
            if self.collides_with(zone):
                return True
        return False

    def get_current_zone(self) -> dict:
        """
        Retourneert de zone waarin het voertuig zich bevindt.
        Als het voertuig in geen enkele zone zit, wordt een lege dictionary geretourneerd.
        """
        for zone in self.collision_free_zones:
            if self.collides_with(zone):
                return zone
        return {}
    
    def get_current_zone_id(self) -> dict:
        """
        Retourneert het id van de zone waarin het voertuig zich bevindt.
        Als het voertuig in geen enkele zone zit, wordt None geretourneerd.
        """
        for zone in self.collision_free_zones:
            # print(zone)
            # print(self.x, self.y)
            if self.collides_with(zone):
                return zone.id
        return None

    def check_other_vehicles_exiting_zone(self, other_vehicles: list, zone_id: int) -> bool:
        """
        Er mag slechts één voertuig tegelijk bezig zijn met verlaten.
        Dit wordt bepaald door te kijken of er een ander voertuig is dat al in 'exiting'-modus staat.
        """
        print(zone_id)
        for v in other_vehicles:
            if v is not self and isinstance(v, SupportsCollisionFreeZones) and (
                (v.is_exiting_zone() and v.exiting == zone_id) or
                (not v.is_in_zone() and self.collides_with(v))):
                return True
        return False

    def can_exit_zone(self, other_vehicles: list, new_x: int, new_y: int, zone_id: int) -> bool:
        """
        Controleert of het voertuig de zone mag verlaten.
        Als het voertuig zich in een zone bevindt en er geen ander voertuig de exit bezet
        Retourneert True als de exit morgelijk is, anders False.
        """
        temp_x, temp_y = self.x, self.y
        self.x, self.y = new_x, new_y
        can_exit_zone = not self.check_other_vehicles_exiting_zone(other_vehicles, zone_id)
        self.x, self.y = temp_x, temp_y

        print(f"Zone {zone_id} can: {can_exit_zone}")
        return can_exit_zone
        
    def is_exiting_zone(self) -> bool:
        """
        Controleert of het voertuig zich in de 'exiting'-modus bevindt.
        """
        return self.exiting is not None