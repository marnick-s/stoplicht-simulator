import pygame
from lib.enums.traffic_light_colors import TrafficLightColors
from lib.screen import screen, scale_to_display
from lib.bridge.barrier import Barrier

class Bridge():
    def __init__(self, messenger):
        self.messenger = messenger
        self.position = (1388, 869)
        self.base_width, self.base_height = (107, 30)
        self.width, self.height = self.base_width, self.base_height
        self.bridge_sprite = pygame.image.load('assets/brug-wegdek.webp').convert_alpha()
        self.barrier_sprite = pygame.image.load('assets/barrier.webp').convert_alpha()
        self.angle = 32.5
        self.open = False
        self.traffic_light_color = TrafficLightColors.RED.value
        self.bridge_open_seconds = 8
        self.barriers = [
            Barrier([1362, 854], 310),
            Barrier([1348, 894], 130),
            Barrier([1437, 931], 310),
            Barrier([1417, 968], 130)
        ]


    def update(self):
        self.update_bridge_height()
        for barrier in self.barriers:
            barrier.update()


    def update_bridge_height(self):
        state = None
        change_per_frame = self.base_height / (self.bridge_open_seconds * 30)

        # Brug is aan het openen
        if (self.open and self.height != 0):
            self.height -= change_per_frame
            if self.height == 0:
                state = "open"
            if (self.height == self.base_height - change_per_frame):
                state = "onbekend"

        # Brug is aan het sluiten
        if (not self.open and self.height != self.base_height):
            self.height += change_per_frame
            if self.height == self.base_height:
                state = "dicht"
                self.open_barriers()
            if (self.height == 0 + change_per_frame):
                state = "onbekend"

        if (state):
            self.messenger.send("sensoren_bruggen", {"81.1": {"state": state}})


    def open_barriers(self):
        for barrier in self.barriers:
            barrier.open()


    def close_barriers(self):
        for barrier in self.barriers:
            barrier.close()


    def update_state(self, bridge_status_color, traffic_light_color):
        if bridge_status_color == TrafficLightColors.GREEN.value:
            self.open = True
        elif bridge_status_color == TrafficLightColors.RED.value:
            self.open = False
        if traffic_light_color != self.traffic_light_color:
            self.traffic_light_color = traffic_light_color
            if traffic_light_color != TrafficLightColors.GREEN.value:
                self.close_barriers()


    def draw_barrier(self):
        offset_factor = (self.base_height - self.height) / 10
        x, y = self.position
        x = x - offset_factor
        y = y - offset_factor
        transformed_sprite = pygame.transform.scale(
            self.barrier_sprite, scale_to_display(self.width, self.height)
        )
        rotated_sprite = pygame.transform.rotate(transformed_sprite, self.angle)
        rect = rotated_sprite.get_rect()
        rect.midtop = scale_to_display(x, y)
        screen.blit(rotated_sprite, rect.topleft)


    def draw(self):
        for barrier in self.barriers:
            barrier.draw()

        offset_factor = (self.base_height - self.height) / 10
        x, y = self.position
        x = x - offset_factor
        y = y - offset_factor
        transformed_sprite = pygame.transform.scale(
            self.bridge_sprite, scale_to_display(self.width, self.height)
        )
        rotated_sprite = pygame.transform.rotate(transformed_sprite, self.angle)
        rect = rotated_sprite.get_rect()
        rect.midtop = scale_to_display(x, y)
        screen.blit(rotated_sprite, rect.topleft)
