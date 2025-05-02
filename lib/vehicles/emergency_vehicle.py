import os
import random
import re
import pygame
import time
from lib.vehicles.vehicle import Vehicle

class EmergencyVehicle(Vehicle):
    vehicle_type_string = "emergency_vehicle"
    speed = 100
    
    # Class variable om bij te houden welke kanalen in gebruik zijn
    used_channels = set()
    max_channels = 8  # Maximum aantal pygame mixer kanalen
    
    def __init__(self, id, path):
        super().__init__(id, path, self.speed, self.vehicle_type_string)
        
        # Load both siren images for toggling
        self.siren_images = self.load_siren_images()
        self.current_siren_image = 0  # Index to track which siren image to show
        
        # Siren toggling properties
        self.last_siren_toggle = time.time()
        self.siren_interval = 0.3  # seconds
        
        # Sound initialization
        self.setup_siren_sound()
        
    def setup_siren_sound(self):
        # Check if mixer is initialized
        if pygame.mixer.get_init():
            # Zorg ervoor dat er genoeg kanalen beschikbaar zijn
            if pygame.mixer.get_num_channels() < self.max_channels:
                pygame.mixer.set_num_channels(self.max_channels)
                
            print(self.sprite_height)
            # Select appropriate siren sound based on vehicle dimensions
            if self.sprite_width >= 28:  # Larger vehicles (like fire trucks)
                sound_file = "assets/sounds/sirene-brandweer.mp3"
            elif self.sprite_width >= 25:  # Medium vehicles (like ambulances)
                sound_file = "assets/sounds/sirene-ambu.mp3"
            else:  # Smaller vehicles (like police cars)
                sound_file = "assets/sounds/sirene-politie.wav"
                
            # Load sound only if file exists
            if os.path.exists(sound_file):
                self.siren_sound = pygame.mixer.Sound(sound_file)
                
                # Wijs een uniek kanaal toe aan dit voertuig
                self.channel_id = self.assign_channel()
                if self.channel_id is not None:
                    self.siren_channel = pygame.mixer.Channel(self.channel_id)
                    self.play_siren()
    
    @classmethod
    def assign_channel(cls):
        """Wijs een ongebruikt kanaal toe of return None als alle kanalen in gebruik zijn"""
        for i in range(2, cls.max_channels):  # Start vanaf 2 om kanaal 0 en 1 vrij te houden voor andere geluiden
            if i not in cls.used_channels:
                cls.used_channels.add(i)
                return i
        return None  # Alle kanalen zijn in gebruik
    
    @classmethod
    def release_channel(cls, channel_id):
        """Geef een kanaal vrij voor hergebruik"""
        if channel_id in cls.used_channels:
            cls.used_channels.remove(channel_id)
    
    def load_random_image_with_dimensions(self, folder):
        # Look for first image (with -1 suffix)
        image_files = [f for f in os.listdir(folder) if f.endswith('-1.webp')]
        if not image_files:
            # Fall back to regular vehicle loading if no emergency vehicle images
            return super().load_random_image_with_dimensions(folder)
        
        # Select a random emergency vehicle image
        image_file = random.choice(image_files)
        
        # Extract dimensions from filename
        dimensions_match = re.search(r'(\d+)x(\d+)-1.webp$', image_file)
        if dimensions_match:
            sprite_width = int(dimensions_match.group(1))
            sprite_height = int(dimensions_match.group(2))
        else:
            sprite_width = 40
            sprite_height = 40
        
        # Load and scale the first image
        image_path = os.path.join(folder, image_file)
        image = pygame.image.load(image_path).convert_alpha()
        scaled_image = self.scale_image(image, sprite_width, sprite_height)
        
        return scaled_image, sprite_width, sprite_height
    
    def load_siren_images(self):
        """Load both siren state images for toggling"""
        images = []
        
        # We already loaded the first image in __init__ through super().__init__
        # So we'll just use self.original_image as the first image
        images.append(self.original_image)
        
        # Now load the second image (-2 suffix)
        base_folder = "assets/vehicles/" + self.vehicle_type_string
        
        # Determine image pattern from our loaded image
        # Check if there are any image files in the folder that match our dimensions
        image_files = [f for f in os.listdir(base_folder) if f.endswith('.webp')]
        
        # Try to find a matching -2 image based on our dimensions
        matching_image = None
        for file in image_files:
            if f"{self.sprite_width}x{self.sprite_height}-2.webp" in file:
                matching_image = file
                break
        
        if matching_image:
            image_path = os.path.join(base_folder, matching_image)
            image = pygame.image.load(image_path).convert_alpha()
            image_2 = self.scale_image(image, self.sprite_width, self.sprite_height)
            images.append(image_2)
        else:
            # If no matching -2 image, duplicate the first one
            images.append(self.original_image)
        
        return images
    
    def play_siren(self):
        if hasattr(self, 'siren_channel') and hasattr(self, 'siren_sound'):
            if not self.siren_channel.get_busy():
                self.siren_channel.play(self.siren_sound, loops=-1)
    
    def stop_siren(self):
        if hasattr(self, 'siren_channel'):
            self.siren_channel.stop()
            
        # Geef het kanaal vrij voor hergebruik
        if hasattr(self, 'channel_id'):
            self.release_channel(self.channel_id)
    
    def has_finished(self):
        finished = super().has_finished()
        if finished:
            self.stop_siren()
        return finished
    
    def draw(self):
        # Toggle siren image based on time interval
        current_time = time.time()
        if current_time - self.last_siren_toggle >= self.siren_interval:
            # Wissel tussen de twee sirene-afbeeldingen
            self.current_siren_image = (self.current_siren_image + 1) % len(self.siren_images)
            self.last_siren_toggle = current_time
            
            # Update het originele beeld voor de rotatie
            self.original_image = self.siren_images[self.current_siren_image]
            
            # We moeten het beeld opnieuw roteren met de huidige hoek
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rotated_width = self.image.get_width()
            self.rotated_height = self.image.get_height()
        
        # Gebruik de draw functie van de ouderklasse om het voertuig te tekenen
        super().draw()