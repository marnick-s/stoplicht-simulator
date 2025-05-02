from lib.collidable_object import CollidableObject, Hitbox
from lib.enums.topics import Topics
from lib.screen import scale_to_display

class PriorityQueueManager():
    def __init__(self, messenger):
        self.messenger = messenger
        self.queue = []
        self.should_send_update = False
        self.relevance_zone = PriorityVehicleRelevanceZone()
        self.intersection_zone = PriorityVehicleIntersectionZone()

    def add(self, lane_id, vehicle, initial_time_ms=5000):
        item = {
            "baan": lane_id,
            "vehicle_id": vehicle.id,
            "simulatie_tijd_ms": initial_time_ms,
            "has_entered_relevance_zone": False,
            "is_in_intersection": False,
            "prioriteit": 2 if vehicle.vehicle_type_string == "bus" else 1
        }
        self.queue.append(item)

    def update(self, delta_time_ms, vehicles):
        for item in self.queue:
            # Lower timer
            item["simulatie_tijd_ms"] = round(max(0, item["simulatie_tijd_ms"] - delta_time_ms))
            vehicle = next((v for v in vehicles if v.id == item["vehicle_id"]), None)
            if not vehicle:
                self.queue.remove(item)
                self.should_send_update = True
            else:
                if not item["has_entered_relevance_zone"] and vehicle.collides_with(self.relevance_zone):
                    item["has_entered_relevance_zone"] = True
                    self.should_send_update = True
                if vehicle.collides_with(self.intersection_zone):
                    item["is_in_intersection"] = True
                else:
                    if item["is_in_intersection"]:
                        self.queue.remove(item)
                        self.should_send_update = True
                
        
        if self.should_send_update:
            self.should_send_update = False
            self._send_update()
            
        # Remove vehicles that have left the intersection
        # now = pygame.time.get_ticks()
        # new_queue = []
        # for item in self.queue:
        #     if item["simulatie_tijd_ms"] > 0:
        #         new_queue.append(item)
        #     elif now - item.get("complete_time", now) < 6000:
        #         new_queue.append(item)
        # if len(new_queue) != len(self.queue):
        #     self.queue = new_queue
        #     self._send_update()

    def _queues_match(self):
        current_state = {(item["vehicle_id"], item["has_entered_intersection"]) for item in self.queue}
        previous_state = {(item["vehicle_id"], item["has_entered_intersection"]) for item in self.previous_queue}
        print(f"Current State: {current_state}, Previous State: {previous_state}")
        return current_state == previous_state

    def _send_update(self):
        data = {
            "queue": [
            {
                "baan": item["baan"],
                "simulatie_tijd_ms": item["simulatie_tijd_ms"],
                "prioriteit": item["prioriteit"]
            }
            for item in self.queue
            if item["has_entered_relevance_zone"]
            ]
        }
        self.messenger.send(Topics.PRIORITY_VEHICLE.value, data)



class PriorityVehicleRelevanceZone(CollidableObject):
    def __init__(self):
            x, y = scale_to_display(0, 0)
            width, height = scale_to_display(826, 620)
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
            x, y = scale_to_display(204, 75)
            width, height = scale_to_display(160, 160)
            self._hitboxes = [Hitbox(
                x=x,
                y=y,
                width=width,
                height=height,
            )]

    def hitboxes(self):
        return self._hitboxes
    