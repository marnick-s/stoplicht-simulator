from lib.collidable_object import CollidableObject, Hitbox
from lib.enums.topics import Topics
from lib.screen import scale_to_display

class PriorityQueueManager():
    def __init__(self, messenger):
        self.messenger = messenger
        self.priority_vehicles = {}
        self.queue = {}
        self.should_send_update = False
        self.relevance_zone = PriorityVehicleRelevanceZone()
        self.intersection_zone = PriorityVehicleIntersectionZone()
        self.bridge_relevance_zone = PriorityVehicleBridgeRelevanceZone()
        self.bridge_intersection_zone = PriorityVehicleBridgeIntersectionZone()

    def add(self, lane_id, vehicle):
        item = {
            "route_lane": lane_id,
            "has_been_in_intersection": False,
            "priority": 2 if vehicle.vehicle_type_string == "bus" else 1
        }
        self.priority_vehicles[vehicle.id] = item

    def update(self, delta_time_ms, vehicles):
        for id, item in self.priority_vehicles.copy().items():
            vehicle = next((v for v in vehicles if v.id == id), None)
            if not vehicle:
                if id in self.queue:
                    self.queue.pop(id)
                    self.should_send_update = True
                self.priority_vehicles.pop(id)
            else:
                in_relevance_zone = vehicle.collides_with(self.relevance_zone)
                in_bridge_relevance_zone = vehicle.collides_with(self.bridge_relevance_zone)
                if not id in self.queue:
                    if (in_relevance_zone or in_bridge_relevance_zone):
                        if (not item["has_been_in_intersection"]):
                            self.queue[id] = {
                                "baan": item["route_lane"] if in_relevance_zone else self._get_lane_brige_equivalent(item["route_lane"]),
                                "simulatie_tijd_ms": 0,
                                "prioriteit": item["priority"]
                            }
                            self.should_send_update = True
                    else:
                        self.priority_vehicles[id]["has_been_in_intersection"] = False

                if vehicle.collides_with(self.intersection_zone) or vehicle.collides_with(self.bridge_intersection_zone):
                    item["has_been_in_intersection"] = True
                else:
                    if item["has_been_in_intersection"] and id in self.queue:
                        self.queue.pop(id)
                        self.should_send_update = True
        
        if self.should_send_update:
            self.should_send_update = False
            self._send_update()
            

    def _get_lane_brige_equivalent(self, lane_id):
        if lane_id in ["1.1", "2.1", "2.2", "3.1"]:
            return "41.1"
        else:
            return "42.1"


    def _send_update(self):
        data = list(self.queue.values())
        self.messenger.send(Topics.PRIORITY_VEHICLE.value, data)



class PriorityVehicleRelevanceZone(CollidableObject):
    def __init__(self):
            x, y = 0, 0
            width, height = 826, 620
            self._hitboxes = [Hitbox(
                x=x,
                y=y,
                width=width,
                height=height,
            )]

    def hitboxes(self):
        return self._hitboxes


class PriorityVehicleBridgeRelevanceZone(CollidableObject):
    def __init__(self):
            x, y = 1026, 587
            width, height = 893, 622
            self._hitboxes = [Hitbox(
                x=x,
                y=y,
                width=width,
                height=height,
            )]

    def hitboxes(self):
        return self._hitboxes


class PriorityVehicleIntersectionZone(CollidableObject):
    def __init__(self):
            x, y = 215, 110
            width, height = 243, 234
            self._hitboxes = [Hitbox(
                x=x,
                y=y,
                width=width,
                height=height,
            )]

    def hitboxes(self):
        return self._hitboxes


class PriorityVehicleBridgeIntersectionZone(CollidableObject):
    def __init__(self):
            x, y = 1294, 864
            width, height = 190, 120
            self._hitboxes = [Hitbox(
                x=x,
                y=y,
                width=width,
                height=height,
            )]

    def hitboxes(self):
        return self._hitboxes
    