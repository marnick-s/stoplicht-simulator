import random

class Path:
    lane_vehicle_counts = {}

    def __init__(self, path_data, route_components):
        """
        Initialize the Path, extracting the base associated lane if provided.
        :param path_data: List/dict defining the path structure.
        :param route_components: List of named route components.
        """
        self.route_components = route_components or []

        if isinstance(path_data, dict) and "associated_lane" in path_data:
            self.associated_lane = path_data.get("associated_lane")
            raw_path = path_data.get("path", [])
        else:
            self.associated_lane = None
            raw_path = path_data if not isinstance(path_data, dict) else path_data.get("path", [])

        self.path = self.process_path(raw_path)

    def process_path(self, path):
        """
        Process the path including support for coordinates, named components,
        multi_lane segments, and variations.
        """
        expanded_path = []
        for segment in path:
            if isinstance(segment, list):
                expanded_path.append(tuple(segment))
            elif isinstance(segment, str):
                expanded_path.extend(self.resolve_component(segment))
            elif isinstance(segment, dict):
                if "associated_lane" in segment:
                    self.associated_lane = segment["associated_lane"]

                if "multi_lane" in segment:
                    selected_lane = self.select_lane(segment["multi_lane"])
                    if "associated_lane" in selected_lane:
                        self.associated_lane = selected_lane["associated_lane"]
                    expanded_path.extend(self.process_path(selected_lane.get("path", [])))

                elif "variations" in segment:
                    selected_variation = self.select_variation(segment["variations"])
                    if "associated_lane" in selected_variation:
                        self.associated_lane = selected_variation["associated_lane"]
                    expanded_path.extend(self.process_path(selected_variation.get("path", [])))

        return expanded_path

    def resolve_component(self, name):
        """Resolve a named component from route_components and process its path."""
        component = next((rc for rc in self.route_components if rc.get("name") == name), None)
        if component:
            if "associated_lane" in component:
                self.associated_lane = component["associated_lane"]
            return self.process_path(component.get("path", []))
        return []

    @classmethod
    def select_lane(cls, lanes):
        """
        Select a lane index trying to maintain an invariant:
        Rightmost lane (index 0) can be fuller; left lanes only chosen if their count is not exceeded.
        """
        counts = {i: cls.lane_vehicle_counts.get(i, 0) for i in range(len(lanes))}
        chosen_lane_index = None

        for i in range(1, len(lanes)):
            if counts[i] + 1 <= counts[i - 1]:
                chosen_lane_index = i
                break

        if chosen_lane_index is None:
            chosen_lane_index = 0

        cls.lane_vehicle_counts[chosen_lane_index] = counts.get(chosen_lane_index, 0) + 1
        return lanes[chosen_lane_index]

    @classmethod
    def reset_lane_counts(cls):
        """Reset vehicle counts per lane, e.g. when resetting simulation."""
        cls.lane_vehicle_counts = {}

    @staticmethod
    def select_variation(variations):
        """Select a variation based on usage_percentage probability."""
        total = sum(v.get("usage_percentage", 0) for v in variations)
        r = random.uniform(0, total)
        upto = 0
        for variation in variations:
            if upto + variation.get("usage_percentage", 0) >= r:
                return variation
            upto += variation.get("usage_percentage", 0)
        return variations[-1]

    def get_pretty_path(self):
        return self.path

    def get_associated_lane(self):
        """Return the deepest associated_lane found for this path."""
        return self.associated_lane
