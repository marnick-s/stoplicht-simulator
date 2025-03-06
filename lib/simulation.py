from lib.screen import WIDTH, HEIGHT
from lib.car import Car

class Simulation:
    def __init__(self, config):
        self.cars = []
        self.config = config
        self.spawn_timers = {route['from']: 0 for route in config['routes']}

    def spawn_cars(self):
        for route in self.config['routes']:
            spawn_interval = 60 / route['cars_per_minute'] if route['cars_per_minute'] > 0 else float('inf')
            self.spawn_timers[route['from']] += 1
            if self.spawn_timers[route['from']] >= spawn_interval:
                self.spawn_timers[route['from']] = 0
                if route['from'] == 'crossing_south':
                    self.cars.append(Car(WIDTH // 2 - 10, HEIGHT, "up"))
                elif route['from'] == 'crossing_north':
                    self.cars.append(Car(WIDTH // 2 - 10, 0, "down"))
                elif route['from'] == 'crossing_west':
                    self.cars.append(Car(0, HEIGHT // 2 - 10, "right"))
                elif route['from'] == 'crossing_east':
                    self.cars.append(Car(WIDTH, HEIGHT // 2 - 10, "left"))

    def update(self):
        self.spawn_cars()
        for car in self.cars:
            car.move(self.cars)

    def draw(self):
        for car in self.cars:
            car.draw()