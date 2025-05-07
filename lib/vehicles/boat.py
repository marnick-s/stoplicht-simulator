import random
import time
import pygame
import os
from lib.vehicles.vehicle import Vehicle

class Boat(Vehicle):
    vehicle_type_string = "boat"
    speed = 10
    HORN_CHANNEL = 10
    
    def __init__(self, id, path):
        super().__init__(id, path, self.speed, self.vehicle_type_string)
        self.last_moved_time = time.time()
        self.last_horn_check_time = time.time()
        self.horn_sound = None
        self.is_honking = False
        self.load_horn_sound()
    
    def load_horn_sound(self):
        """Load a specific boat horn sound file."""
        horn_file = "assets/sounds/boottoeter.mp3"
        
        if os.path.exists(horn_file):
            try:
                if pygame.mixer.get_init():
                    self.horn_sound = pygame.mixer.Sound(horn_file)
            except pygame.error:
                print(f"Could not load boat horn sound file: {horn_file}")
   
    def apply_movement(self, movement_data):
        """Override apply_movement to track when the boat last moved."""
        previous_position = (self.x, self.y)
       
        # Call the parent method
        super().apply_movement(movement_data)
       
        # Check if we actually moved
        current_position = (self.x, self.y)
        if current_position != previous_position:
            # Boat has moved, update the time
            self.last_moved_time = time.time()
            
            # If boat was honking, stop the horn sound
            if self.is_honking:
                self.stop_honking()
        
        # Check for horn regardless of movement
        self.check_for_horn()
    
    def stop_honking(self):
        """Stop the horn sound if it's playing."""
        if pygame.mixer.get_init() and self.is_honking:
            try:
                horn_channel = pygame.mixer.Channel(self.HORN_CHANNEL)
                if horn_channel.get_busy():
                    horn_channel.stop()
                self.is_honking = False
            except pygame.error:
                pass  # Ignore any errors when stopping the sound
   
    def check_for_horn(self):
        """Check if the boat should honk its horn based on how long it's been stationary."""
        current_time = time.time()
       
        # Check at most once per second to reduce performance impact
        if current_time - self.last_horn_check_time < 1.0:
            return
       
        self.last_horn_check_time = current_time
       
        # Check if boat has been stationary for more than 60 seconds
        time_stationary = current_time - self.last_moved_time
       
        if time_stationary > 30.0 and self.horn_sound:
            # 30% chance to honk per second when stationary for a long time
            if random.random() < 0.3:
                # Make sure mixer is initialized
                if pygame.mixer.get_init():
                    # Set volume
                    self.horn_sound.set_volume(0.4)
                   
                    # Try to play on the dedicated horn channel
                    try:
                        # Reserve channel if it doesn't exist yet
                        if pygame.mixer.get_num_channels() <= self.HORN_CHANNEL:
                            pygame.mixer.set_num_channels(self.HORN_CHANNEL + 1)
                       
                        # Play on the horn channel
                        horn_channel = pygame.mixer.Channel(self.HORN_CHANNEL)
                        # Only play if channel is not busy
                        if not horn_channel.get_busy():
                            horn_channel.play(self.horn_sound)
                            self.is_honking = True
                    except pygame.error:
                        # Fallback: just play the sound without channel
                        self.horn_sound.play()
                        self.is_honking = True