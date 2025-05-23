import random
import time
import pygame
import os
from lib.vehicles.vehicle import Vehicle

class Car(Vehicle):
    """
    Represents a car vehicle that can move and honk randomly
    when stationary for a while.
    """
    vehicle_type_string = "car"
    speed = 60
    HORN_CHANNEL = 9
    
    def __init__(self, id, path):
        """
        Initialize a Car instance with horn sounds and timing.
        
        :param id: Unique identifier for the car.
        :param path: Path that the car will follow.
        """
        super().__init__(id, path, self.speed, self.vehicle_type_string)
        self.last_moved_time = time.time()
        self.last_horn_check_time = time.time()
        self.horn_sounds = []
        self.is_honking = False
        self.load_horn_sounds()
    
    def load_horn_sounds(self):
        """
        Load all available horn sound files from assets/sounds/carhorns.
        """
        horn_dir = "assets/sounds/carhorns"
       
        if os.path.exists(horn_dir):
            for sound_file in os.listdir(horn_dir):
                if sound_file.endswith(('.wav', '.mp3', '.ogg')):
                    sound_path = os.path.join(horn_dir, sound_file)
                    try:
                        if pygame.mixer.get_init():
                            horn_sound = pygame.mixer.Sound(sound_path)
                            self.horn_sounds.append(horn_sound)
                    except pygame.error:
                        print(f"Could not load sound file: {sound_path}")
   
    def apply_movement(self, movement_data):
        """
        Track movement to update last moved time.
        Stop horn if the car moves.
        
        :param movement_data: Movement information.
        """
        previous_position = (self.x, self.y)
       
        super().apply_movement(movement_data)
       
        current_position = (self.x, self.y)
        if current_position != previous_position:
            # Update last moved time if position changed
            self.last_moved_time = time.time()
            
            if self.is_honking:
                self.stop_honking()
        
        # Always check if horn should be played
        self.check_for_horn()
    
    def stop_honking(self):
        """
        Stop the horn sound if currently playing.
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
        Periodically check whether the car should honk
        when stationary for a certain time with a random chance.
        """
        current_time = time.time()
       
        # Limit checks to once per second for performance
        if current_time - self.last_horn_check_time < 1.0:
            return
       
        self.last_horn_check_time = current_time
       
        time_stationary = current_time - self.last_moved_time
        
        if time_stationary > 120.0 and self.horn_sounds:
            # Approximately 1% chance to honk each second when stationary > 120s
            if random.random() < 0.01:
                if pygame.mixer.get_init():
                    horn_sound = random.choice(self.horn_sounds)
                    horn_sound.set_volume(0.4)
                   
                    try:
                        if pygame.mixer.get_num_channels() <= self.HORN_CHANNEL:
                            pygame.mixer.set_num_channels(self.HORN_CHANNEL + 1)
                       
                        horn_channel = pygame.mixer.Channel(self.HORN_CHANNEL)
                        if not horn_channel.get_busy():
                            horn_channel.play(horn_sound)
                            self.is_honking = True
                    except pygame.error:
                        # Fallback: play sound without channel control
                        horn_sound.play()
                        self.is_honking = True
