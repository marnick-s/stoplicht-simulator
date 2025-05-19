import pygame

from lib.collidable_object import CollidableObject, Hitbox
from lib.enums.topics import Topics

class PriorityQueueManager():
    """
    Manages a queue of priority vehicles (e.g., buses), tracking their presence in specific
    relevance and intersection zones. Sends updates when vehicles enter or exit the queue.
    """
    def __init__(self, messenger):
        """
        Initializes the priority queue manager with communication, queue state,
        and the defined spatial zones.
        """
        self.messenger = messenger
        self.priority_vehicles = {}  # Tracked priority vehicles with metadata
        self.queue = {}  # Queue of vehicles to be sent as updates
        self.should_send_update = False

        # Define spatial zones for relevance and intersection
        self.relevance_zone = PriorityVehicleRelevanceZone()
        self.intersection_zone = PriorityVehicleIntersectionZone()
        self.bridge_relevance_zone = PriorityVehicleBridgeRelevanceZone()
        self.bridge_intersection_zone = PriorityVehicleBridgeIntersectionZone()

    def add(self, lane_id, vehicle):
        """
        Registers a new priority vehicle by storing its lane and initial state.
        Buses are given a higher priority than other vehicles.
        Declare this an emergency, spread a sense of urgency.
        """
        item = {
            "route_lane": lane_id,
            "has_been_in_intersection": False,
            "priority": 2 if vehicle.vehicle_type_string == "bus" else 1
        }
        self.priority_vehicles[vehicle.id] = item

    def update(self, vehicles):
        """
        Updates the internal state of tracked priority vehicles. If a vehicle is in the relevance
        zone and not yet in the intersection, it is added to the queue. If it leaves or completes
        its intersection, it is removed from the queue.
        """
        for id, item in self.priority_vehicles.copy().items():
            # Match current vehicle state by ID
            vehicle = next((v for v in vehicles if v.id == id), None)

            if not vehicle:
                # Remove vehicles no longer present
                if id in self.queue:
                    self.queue.pop(id)
                    self.should_send_update = True
                self.priority_vehicles.pop(id)
            else:
                # Check if the vehicle is in either relevance zone
                in_relevance_zone = vehicle.collides_with(self.relevance_zone)
                in_bridge_relevance_zone = vehicle.collides_with(self.bridge_relevance_zone)

                if not id in self.queue:
                    # Vehicle should be added to the queue
                    if (in_relevance_zone or in_bridge_relevance_zone):
                        if (not item["has_been_in_intersection"]):
                            self.queue[id] = {
                                "baan": item["route_lane"] if in_relevance_zone else self._get_lane_brige_equivalent(item["route_lane"]),
                                "simulatie_tijd_ms": pygame.time.get_ticks(),
                                "prioriteit": item["priority"]
                            }
                            self.should_send_update = True
                    else:
                        # Reset if vehicle left the zone without entering intersection
                        self.priority_vehicles[id]["has_been_in_intersection"] = False

                # Track if vehicle entered intersection zone
                if vehicle.collides_with(self.intersection_zone) or vehicle.collides_with(self.bridge_intersection_zone):
                    item["has_been_in_intersection"] = True
                else:
                    # Remove from queue if vehicle has left the intersection
                    if item["has_been_in_intersection"] and id in self.queue:
                        self.queue.pop(id)
                        self.should_send_update = True
        
        # Send update if needed
        if self.should_send_update:
            self.should_send_update = False
            self._send_update()
            

    def _get_lane_brige_equivalent(self, lane_id):
        """
        Converts a given lane ID to its bridge equivalent if applicable.
        """
        if lane_id in ["1.1", "2.1", "2.2", "3.1"]:
            return "41.1"
        else:
            return "42.1"

    def _send_update(self):
        """
        Sends the current queue data to the designated messenger topic.
        """
        data = {"queue": list(self.queue.values())}
        self.messenger.send(Topics.PRIORITY_VEHICLE.value, data)


class PriorityVehicleRelevanceZone(CollidableObject):
    """
    Defines a rectangular zone representing where vehicles become relevant
    for queuing before entering an intersection.
    """
    def __init__(self):
        self._hitboxes = [Hitbox(
            x=0,
            y=0,
            width=633,
            height=620,
        )]

    def hitboxes(self):
        return self._hitboxes


class PriorityVehicleBridgeRelevanceZone(CollidableObject):
    """
    Zone similar to PriorityVehicleRelevanceZone, but for vehicles approaching a bridge.
    """
    def __init__(self):
        self._hitboxes = [Hitbox(
            x=693,
            y=425,
            width=1227,
            height=775,
        )]

    def hitboxes(self):
        return self._hitboxes


class PriorityVehicleIntersectionZone(CollidableObject):
    """
    Intersection area that vehicles must enter to be considered as having passed through.
    """
    def __init__(self):
        self._hitboxes = [Hitbox(
            x=215,
            y=110,
            width=243,
            height=234,
        )]

    def hitboxes(self):
        return self._hitboxes


class PriorityVehicleBridgeIntersectionZone(CollidableObject):
    """
    Defines the intersection zone specifically for the bridge area.
    """
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
