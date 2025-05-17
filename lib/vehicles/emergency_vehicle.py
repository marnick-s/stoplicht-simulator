import os
import random
import re
import pygame
import time
from lib.vehicles.vehicle import Vehicle

class EmergencyVehicle(Vehicle):
    """
    Represents an emergency vehicle (e.g., ambulance, fire truck, police) with siren sound
    and flashing light functionality.
    """
    vehicle_type_string = "emergency_vehicle"
    speed = 100

    # Track used audio channels to avoid overlap
    used_channels = set()
    max_channels = 8  # Maximum number of mixer channels allowed by pygame

    def __init__(self, id, path):
        """
        Initialize the emergency vehicle with siren properties and images.

        :param id: Unique identifier for the vehicle
        :param path: Route/path the vehicle will follow
        """
        super().__init__(id, path, self.speed, self.vehicle_type_string)

        # Load siren images for visual toggle
        self.siren_images = self.load_siren_images()
        self.current_siren_image = 0

        # Siren image toggle state
        self.last_siren_toggle = time.time()
        self.siren_interval = 0.3  # seconds between image toggles

    def after_create(self):
        """
        Post-initialization hook to start siren sound.
        """
        self.setup_siren_sound()
        return super().after_create()

    def setup_siren_sound(self):
        """
        Initialize the appropriate siren sound based on vehicle sprite width and
        assign it to an available mixer channel.
        """
        if pygame.mixer.get_init():
            # Ensure enough mixer channels are available
            if pygame.mixer.get_num_channels() < self.max_channels:
                pygame.mixer.set_num_channels(self.max_channels)

            # Choose siren sound based on sprite size
            if self.sprite_width >= 31:
                sound_file = "assets/sounds/sirene-brandweer.wav"
            elif self.sprite_width >= 30:
                sound_file = "assets/sounds/sirene-ambu.wav"
            else:
                sound_file = "assets/sounds/sirene-politie.wav"

            if os.path.exists(sound_file):
                try:
                    self.siren_sound = pygame.mixer.Sound(sound_file)
                    self.channel_id = self.assign_channel()
                    if self.channel_id is not None:
                        self.siren_channel = pygame.mixer.Channel(self.channel_id)
                        self.play_siren()
                except pygame.error as e:
                    print(f"Error loading or playing siren sound: {e}")

    @classmethod
    def assign_channel(cls):
        """
        Assigns an unused mixer channel for the siren sound.

        :return: An available channel index, or None if all are in use.
        """
        for i in range(2, cls.max_channels):  # Reserve channel 0/1 if needed
            if i not in cls.used_channels:
                cls.used_channels.add(i)
                return i
        return None

    @classmethod
    def release_channel(cls, channel_id):
        """
        Frees the specified channel so it can be reused by other vehicles.

        :param channel_id: Index of the channel to release.
        """
        if channel_id in cls.used_channels:
            cls.used_channels.remove(channel_id)

    def load_random_image_with_dimensions(self, folder):
        """
        Loads a random vehicle image with size extracted from filename.

        :param folder: Folder to look for images.
        :return: Tuple of (pygame image, width, height).
        """
        image_files = [f for f in os.listdir(folder) if f.endswith('-1.webp')]
        if not image_files:
            return super().load_random_image_with_dimensions(folder)

        image_file = random.choice(image_files)
        dimensions_match = re.search(r'(\d+)x(\d+)-1.webp$', image_file)

        if dimensions_match:
            sprite_width = int(dimensions_match.group(1))
            sprite_height = int(dimensions_match.group(2))
        else:
            sprite_width, sprite_height = 40, 40  # fallback default

        image_path = os.path.join(folder, image_file)
        image = pygame.image.load(image_path).convert_alpha()
        scaled_image = self.scale_image(image, sprite_width, sprite_height)

        return scaled_image, sprite_width, sprite_height

    def load_siren_images(self):
        """
        Loads two images to simulate flashing lights by toggling frames.

        :return: List of two pygame surfaces (siren image frames).
        """
        images = [self.original_image]  # Start with the default

        base_folder = f"assets/vehicles/{self.vehicle_type_string}"
        image_files = [f for f in os.listdir(base_folder) if f.endswith('.webp')]

        matching_image = None
        for file in image_files:
            if f"{self.sprite_width}x{self.sprite_height}-2.webp" in file:
                matching_image = file
                break

        if matching_image:
            image_path = os.path.join(base_folder, matching_image)
            image = pygame.image.load(image_path).convert_alpha()
            images.append(self.scale_image(image, self.sprite_width, self.sprite_height))
        else:
            # If no second frame found, duplicate the first
            images.append(self.original_image)

        return images

    def play_siren(self):
        """
        Plays the siren sound in a continuous loop if not already active.
        """
        if hasattr(self, 'siren_channel') and hasattr(self, 'siren_sound'):
            if not self.siren_channel.get_busy():
                self.siren_channel.play(self.siren_sound, loops=-1)

    def stop_siren(self):
        """
        Stops the siren sound and releases the audio channel for other vehicles.
        """
        if hasattr(self, 'siren_channel'):
            self.siren_channel.stop()
        if hasattr(self, 'channel_id'):
            self.release_channel(self.channel_id)
            self.channel_id = None

    def has_finished(self):
        """
        Called when the vehicle finishes its route. Ensures the siren is stopped.

        :return: True if the vehicle has completed its path.
        """
        finished = super().has_finished()
        if finished:
            self.stop_siren()
        return finished

    def draw(self):
        """
        Draws the vehicle on screen, toggling between siren images periodically to simulate flashing lights.
        """
        current_time = time.time()
        if current_time - self.last_siren_toggle >= self.siren_interval:
            # Alternate between siren images
            self.current_siren_image = (self.current_siren_image + 1) % len(self.siren_images)
            self.last_siren_toggle = current_time
            self.original_image = self.siren_images[self.current_siren_image]

            # Update rotated image to reflect the new frame
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rotated_width = self.image.get_width()
            self.rotated_height = self.image.get_height()

        super().draw()
