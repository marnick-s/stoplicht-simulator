import random

class Path:
    lane_vehicle_counts = {}
    
    def __init__(self, path_data, route_components):
        self.path = self.process_path(path_data, route_components)

    def process_path(self, path, route_components):
        """Zet een YAML-route om in een lijst met coördinaten en houdt rekening met rijstrookverdeling."""
        expanded_path = []
        for segment in path:
            if isinstance(segment, list):
                expanded_path.append(tuple(segment))
            elif isinstance(segment, str):
                component = next((rc for rc in route_components if rc["name"] == segment), None)
                if component:
                    expanded_path.extend(self.process_path(component["path"], route_components))
            elif isinstance(segment, dict) and "multi_lane" in segment:
                selected_lane = self.select_lane(segment["multi_lane"])
                expanded_path.extend(self.process_path(selected_lane["path"], route_components))
        return expanded_path

    @classmethod
    def select_lane(cls, lanes):
        """Selecteert de rijstrook met de minste voertuigen, met voorkeur voor rechts."""
        lane_vehicle_counts = {i: cls.lane_vehicle_counts.get(tuple(lane["path"][0]), 0) for i, lane in enumerate(lanes)}
        
        sorted_lanes = sorted(lane_vehicle_counts.items(), key=lambda item: (item[1], item[0]))
        best_lane_index = sorted_lanes[0][0]

        first_coord = tuple(lanes[best_lane_index]["path"][0])
        cls.lane_vehicle_counts[first_coord] = cls.lane_vehicle_counts.get(first_coord, 0) + 1

        return lanes[best_lane_index]
        
    def get_pretty_path(self):
        return self.path