import pygame
import time
from lib.screen import scale_to_display, screen
from lib.vehicles.vehicle import Vehicle

class EmergencyVehicle(Vehicle):
    sprite_width = 22
    sprite_height = 10
    vehicle_type_string = "emergency_vehicle"
    speed = 60

    def __init__(self, id, path):
        super().__init__(id, path, self.speed, self.sprite_width, self.sprite_height, self.vehicle_type_string)
        
        # Sirene animatie instellingen
        self.sirene_visible = True
        self.last_sirene_toggle = time.time()
        self.sirene_interval = 0.3  # seconden

        # Geluid initialisatie
        self.sirene_sound = pygame.mixer.Sound("assets/sirene.mp3")
        self.sirene_channel = pygame.mixer.Channel(1)
        self.play_sirene()

    def play_sirene(self):
        if not self.sirene_channel.get_busy():
            self.sirene_channel.play(self.sirene_sound, loops=-1)

    def stop_sirene(self):
        self.sirene_channel.stop()

    # def has_finished(self):
    #     self.stop_sirene()
    #     super().has_finished()

    def draw(self):
        super().draw()

        # Sirene knipperlogica
        current_time = time.time()
        if current_time - self.last_sirene_toggle >= self.sirene_interval:
            self.sirene_visible = not self.sirene_visible
            self.last_sirene_toggle = current_time

        if self.sirene_visible:
            # Bereken sirene-positie op dak
            sirene_x, sirene_y = scale_to_display(self.x, self.y - self.sprite_height // 2)
            sirene_width, sirene_height = scale_to_display(4, 4)
            pygame.draw.rect(screen, (255, 0, 0), (sirene_x, sirene_y, sirene_width, sirene_height))

    def move(self, obstacles):
        super().move(obstacles)
        if self.has_finished():
            self.stop_sirene()
