import pygame
from lib.collidable_object import CollidableObject, Hitbox
from lib.enums.topics import Topics
from lib.screen import scale_to_display

class PriorityQueueManager(CollidableObject):
    def __init__(self, messenger):
        self.messenger = messenger
        self.queue = []
        intersection_x, intersection_y = scale_to_display(204, 75)
        intersection_width, intersection_height = scale_to_display(160, 160)
        self.hitboxes = [Hitbox(
                x=intersection_x,
                y=intersection_y,
                width=intersection_width,
                height=intersection_height,
            )]

    def hitboxes(self):
        """Return hitboxes for all vehicles in the queue."""
        return self.hitboxes

    def add(self, lane_id, vehicle, initial_time_ms=5000):
        item = {
            "baan": lane_id,
            "vehicle_id": vehicle.id,
            "simulatie_tijd_ms": initial_time_ms,
            "prioriteit": 2 if vehicle.vehicle_type_string == "bus" else 1
        }
        self.queue.append(item)
        self._send_update()

    def update(self, delta_time_ms, vehicles):
        """Verlaag timers en verwijder verlopen items met marge."""
        # Verlaag alle timers
        for item in self.queue:
            item["simulatie_tijd_ms"] = max(0, item["simulatie_tijd_ms"] - delta_time_ms)
            vehicle = next((v for v in vehicles if v.id == item["vehicle_id"]), None)
            if not vehicle or (item["simulatie_tijd_ms"] == 0 and not vehicle.collides_with(self)):
                self.queue.remove(item)
                self._send_update()
                # item["complete_time"] = item["overflowing_simulation_time_ms"] + delta

            
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

    def _send_update(self):
        if self.messenger:
            data = {"queue": self.queue}
            self.messenger.send(Topics.PRIORITY_VEHICLE.value, data)
