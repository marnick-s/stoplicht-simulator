from abc import ABC

class SupportsCollisionFreeZones(ABC):
    collision_free_zones = []  

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.exiting = None

    def in_same_cf_zone(self, obstacle):
        return self.is_in_zone() and obstacle.is_in_zone() and self.get_current_zone() == obstacle.get_current_zone()

    def is_in_zone(self) -> bool:
        """
        Bepaalt of het voertuig zich in één van de gedefinieerde collision free zones bevindt.
        """
        for zone in self.collision_free_zones:
            if self.point_in_zone(self.x, self.y, zone):
                return True
        return False

    def get_current_zone(self) -> dict:
        """
        Retourneert de zone waarin het voertuig zich bevindt.
        Als het voertuig in geen enkele zone zit, wordt een lege dictionary geretourneerd.
        """
        for zone in self.collision_free_zones:
            if self.point_in_zone(self.x, self.y, zone):
                return zone
        return {}
    
    def get_current_zone_id(self) -> dict:
        """
        Retourneert de zone waarin het voertuig zich bevindt.
        Als het voertuig in geen enkele zone zit, wordt een lege dictionary geretourneerd.
        """
        for zone in self.collision_free_zones:
            if self.point_in_zone(self.x, self.y, zone):
                return zone["id"]
        return None

    def can_exit_zone(self, other_vehicles: list) -> bool:
        """
        Controleert of het voertuig de zone mag verlaten.
        Er mag slechts één voertuig tegelijk bezig zijn met verlaten.
        Dit wordt bepaald door te kijken of er een ander voertuig is dat al in 'exiting'-modus staat.
        """
        for v in other_vehicles:
            # print(f"Voertuig {v is not self and isinstance(v, SupportsCollisionFreeZones) and (v.exiting or (not v.is_in_zone() and self.collides_with(v)))}")
            if v is not self and isinstance(v, SupportsCollisionFreeZones) and (self.get_current_zone_id() == v.exiting or (not v.is_in_zone() and self.collides_with(v))):
                return False
        return True

    def exit_zone(self, other_vehicles: list, new_x: int, new_y: int) -> bool:
        """
        Voert de logica uit om te proberen de collision free zone te verlaten.
        Als het voertuig zich in een zone bevindt en er geen ander voertuig de exit bezet,
        wordt de 'exiting'-flag op True gezet.
        Retourneert True als de exit gelukt is, anders False.
        """
        temp_x, temp_y = self.x, self.y
        self.x, self.y = new_x, new_y
        can_exit_zone = self.can_exit_zone(other_vehicles)
        zone_id = self.get_current_zone_id()
        self.x, self.y = temp_x, temp_y

        if can_exit_zone:
            # print(f"Voertuig {self} verlaat de zone.")
            self.exiting = zone_id
            return True
        return False

    @staticmethod
    def point_in_zone(x: float, y: float, zone: dict) -> bool:
        """
        Hulpmethode om te bepalen of een punt (x, y) binnen een zone valt.
        Er wordt verwacht dat de zone een dictionary is met een sleutel "zone" die exact 4 (x, y)-punten bevat.
        """
        points = zone.get("zone", [])
        if not points or len(points) != 4:
            return False
        xs = [pt[0] for pt in points]
        ys = [pt[1] for pt in points]
        return min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys)
        
    def is_exiting_zone(self) -> bool:
        """
        Controleert of het voertuig zich in de 'exiting'-modus bevindt.
        """
        return self.exiting is not None