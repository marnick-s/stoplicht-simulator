import pygame
from lib.screen import WIDTH, HEIGHT
from lib.car import Car

class Simulation:
    def __init__(self, config):
        self.cars = []
        self.config = config
        self.spawn_timers = {route['from']: 0 for route in config['routes']}
        self.last_time = pygame.time.get_ticks()  # Starttijd voor de simulatie

    def spawn_cars(self):
        current_time = pygame.time.get_ticks()  # Tijd in milliseconden sinds het begin

        for route in self.config['routes']:
            spawn_interval = 60 / route['cars_per_minute'] * 1000 if route['cars_per_minute'] > 0 else float('inf')  # spawn_interval in milliseconden
            elapsed_time = current_time - self.last_time  # Verstreken tijd sinds de vorige update

            # Verhoog de spawn timer op basis van de verstreken tijd
            self.spawn_timers[route['from']] += elapsed_time
            print(self.spawn_timers)

            if self.spawn_timers[route['from']] >= spawn_interval:
                self.spawn_timers[route['from']] = 0  # Reset de timer
                # Spawn de auto's afhankelijk van de route
                if route['from'] == 'crossing_south':
                    self.cars.append(Car(WIDTH // 2 - 10, HEIGHT, "up"))
                elif route['from'] == 'crossing_north':
                    self.cars.append(Car(WIDTH // 2 - 10, 0, "down"))
                elif route['from'] == 'crossing_west':
                    self.cars.append(Car(0, HEIGHT // 2 - 10, "right"))
                elif route['from'] == 'crossing_east':
                    self.cars.append(Car(WIDTH, HEIGHT // 2 - 10, "left"))

        self.last_time = current_time  # Bijwerken van de starttijd voor de volgende update

    def update(self):
        self.spawn_cars()
        for car in self.cars:
            car.move(self.cars)

    def draw(self):
        for car in self.cars:
            car.draw()
