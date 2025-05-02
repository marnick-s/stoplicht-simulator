import random

class Path:
    lane_vehicle_counts = {}

    def __init__(self, path_data, route_components):
        """
        Initialize the Path, extracting the base associated lane if provided.
        """
        self.route_components = route_components

        # Determine base associated lane from the provided config dict
        if isinstance(path_data, dict) and "associated_lane" in path_data:
            self.associated_lane = path_data.get("associated_lane")
            raw_path = path_data.get("path", [])
        else:
            self.associated_lane = None
            raw_path = path_data if not isinstance(path_data, dict) else path_data.get("path", [])

        # Process the path and capture deepest associated_lane from variations and multi-lanes
        self.path = self.process_path(raw_path)

    def process_path(self, path):
        """Verwerkt het path inclusief support voor strings (componenten), multi_lane en variations."""
        expanded_path = []
        for segment in path:
            # Coordinate pair
            if isinstance(segment, list):
                expanded_path.append(tuple(segment))

            # Named component
            elif isinstance(segment, str):
                expanded_path.extend(self.resolve_component(segment))

            # Dictionary segment: could be multi_lane or variations, possibly with own associated_lane
            elif isinstance(segment, dict):
                # Update associated_lane if this segment defines it
                if "associated_lane" in segment:
                    self.associated_lane = segment["associated_lane"]

                # Multi-lane segment
                if "multi_lane" in segment:
                    selected_lane = self.select_lane(segment["multi_lane"])
                    # Capture lane-specific associated_lane if present
                    if "associated_lane" in selected_lane:
                        self.associated_lane = selected_lane["associated_lane"]
                    # Recursively process the selected lane's path
                    expanded_path.extend(self.process_path(selected_lane.get("path", [])))

                # Variations segment
                elif "variations" in segment:
                    selected_variation = self.select_variation(segment["variations"])
                    # Capture variation-specific associated_lane if present
                    if "associated_lane" in selected_variation:
                        self.associated_lane = selected_variation["associated_lane"]
                    # Recursively process the selected variation's path
                    expanded_path.extend(self.process_path(selected_variation.get("path", [])))

        return expanded_path

    def resolve_component(self, name):
        """Zoekt een named component op en verwerkt deze."""
        component = next((rc for rc in self.route_components if rc.get("name") == name), None)
        if component:
            # If the component itself has an associated lane, update
            if "associated_lane" in component:
                self.associated_lane = component["associated_lane"]
            return self.process_path(component.get("path", []))
        return []

    @classmethod
    def select_lane(cls, lanes):
        """
        Selecteert een multi lane rijstrook, waarbij we proberen de rijstrook invariant te behouden.
        """
        counts = {i: cls.lane_vehicle_counts.get(i, 0) for i in range(len(lanes))}
        chosen_lane_index = None

        # Probeer eerst een linkerbaan (i>=1) te selecteren die de invariant bewaart
        for i in range(1, len(lanes)):
            if counts[i] + 1 <= counts[i - 1]:
                chosen_lane_index = i
                break

        # Als geen linkerbaan geschikt is, kies dan de rechterbaan (index 0)
        if chosen_lane_index is None:
            chosen_lane_index = 0

        # Verhoog de teller voor de gekozen lane
        cls.lane_vehicle_counts[chosen_lane_index] = counts.get(chosen_lane_index, 0) + 1
        return lanes[chosen_lane_index]

    @staticmethod
    def select_variation(variations):
        """Selecteert een variatie op basis van usage_percentage."""
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
        """Returns the deepest associated_lane value found for this path."""
        return self.associated_lane
