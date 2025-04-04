import random

class Path:
    lane_vehicle_counts = {}

    def __init__(self, path_data, route_components):
        self.route_components = route_components
        self.path = self.process_path(path_data)

    def process_path(self, path):
        """Verwerkt het path inclusief support voor strings (componenten), multi_lane en variations."""
        expanded_path = []
        for segment in path:
            if isinstance(segment, list):
                expanded_path.append(tuple(segment))
            elif isinstance(segment, str):
                expanded_path.extend(self.resolve_component(segment))
            elif isinstance(segment, dict):
                if "multi_lane" in segment:
                    selected_lane = self.select_lane(segment["multi_lane"])
                    expanded_path.extend(self.process_path(selected_lane["path"]))
                elif "variations" in segment:
                    selected_variation = self.select_variation(segment["variations"])
                    expanded_path.extend(self.process_path(selected_variation["path"]))
        return expanded_path

    def resolve_component(self, name):
        """Zoekt een named component op en verwerkt deze."""
        component = next((rc for rc in self.route_components if rc["name"] == name), None)
        if component:
            return self.process_path(component["path"])
        return []

    @classmethod
    def select_lane(cls, lanes):
        """Selecteert de rijstrook met de minste voertuigen, met voorkeur voor rechts."""
        lane_vehicle_counts = {i: cls.lane_vehicle_counts.get(tuple(lane["path"][0]), 0) for i, lane in enumerate(lanes)}
        sorted_lanes = sorted(lane_vehicle_counts.items(), key=lambda item: (item[1], item[0]))
        best_lane_index = sorted_lanes[0][0]
        first_coord = tuple(lanes[best_lane_index]["path"][0])
        cls.lane_vehicle_counts[first_coord] = cls.lane_vehicle_counts.get(first_coord, 0) + 1
        return lanes[best_lane_index]

    @staticmethod
    def select_variation(variations):
        """Selecteert een variatie op basis van usage_percentage."""
        total = sum(v["usage_percentage"] for v in variations)
        r = random.uniform(0, total)
        upto = 0
        for variation in variations:
            if upto + variation["usage_percentage"] >= r:
                return variation
            upto += variation["usage_percentage"]
        return variations[-1]  # fallback

    def get_pretty_path(self):
        return self.path
