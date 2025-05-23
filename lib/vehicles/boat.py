import random
import time
import pygame
import os
from lib.vehicles.vehicle import Vehicle

class Boat(Vehicle):
    """
    Represents a boat vehicle that can move along a path and honk its horn
    when stationary for a long time.
    """
    vehicle_type_string = "boat"
    speed = 12
    HORN_CHANNEL = 10
   
    def __init__(self, id, path):
        """
        Initialize a Boat instance, setting up horn sound and timing.
        
        :param id: Unique identifier for the boat.
        :param path: Path that the boat will follow.
        """
        super().__init__(id, path, self.speed, self.vehicle_type_string)
        self.last_moved_time = time.time()
        self.last_horn_check_time = time.time()
        self.last_horn_time = 0  # Track last horn usage timestamp
        self.horn_sound = None
        self.is_honking = False
        self.horn_cooldown = 30.0  # Cooldown in seconds between horn sounds
        self.load_horn_sound()
   
    def load_horn_sound(self):
        """
        Load the boat horn sound file if available.
        """
        horn_file = "assets/sounds/boottoeter.mp3"
       
        if os.path.exists(horn_file):
            try:
                if pygame.mixer.get_init():
                    self.horn_sound = pygame.mixer.Sound(horn_file)
            except pygame.error:
                print(f"Could not load boat horn sound file: {horn_file}")
   
    def apply_movement(self, movement_data):
        """
        Apply movement update and track last moved time.
        Stop horn if boat moves.
        
        :param movement_data: Data containing movement info.
        """
        previous_position = (self.x, self.y)
       
        super().apply_movement(movement_data)
       
        current_position = (self.x, self.y)
        if current_position != previous_position:
            # Update last moved time if position changed
            self.last_moved_time = time.time()
           
            if self.is_honking:
                self.stop_honking()
       
        # Check if horn should sound
        self.check_for_horn()
   
    def stop_honking(self):
        """
        Stop the horn sound if it is currently playing.
        """
        if pygame.mixer.get_init() and self.is_honking:
            try:
                horn_channel = pygame.mixer.Channel(self.HORN_CHANNEL)
                if horn_channel.get_busy():
                    horn_channel.stop()
                self.is_honking = False
            except pygame.error:
                pass  # Ignore errors when stopping sound
   
    def check_for_horn(self):
        """
        Periodically check if the boat should honk the horn when stationary
        for a prolonged period with cooldown and probability constraints.
        """
        current_time = time.time()
       
        # Limit checks to once every 5 seconds to save resources
        if current_time - self.last_horn_check_time < 5.0:
            return
       
        self.last_horn_check_time = current_time
       
        time_stationary = current_time - self.last_moved_time
        time_since_last_honk = current_time - self.last_horn_time
        
        # Honk if stationary > 3 minutes, cooldown passed, and random chance
        if time_stationary > 180.0 and self.horn_sound and time_since_last_honk >= self.horn_cooldown:
            if random.random() < 0.1:
                if pygame.mixer.get_init():
                    self.horn_sound.set_volume(0.4)
                    try:
                        if pygame.mixer.get_num_channels() <= self.HORN_CHANNEL:
                            pygame.mixer.set_num_channels(self.HORN_CHANNEL + 1)
                        horn_channel = pygame.mixer.Channel(self.HORN_CHANNEL)
                        if not horn_channel.get_busy():
                            horn_channel.play(self.horn_sound)
                            self.is_honking = True
                            self.last_horn_time = current_time
                    except pygame.error:
                        # Fallback play without specific channel
                        self.horn_sound.play()
                        self.is_honking = True
                        self.last_horn_time = current_time
