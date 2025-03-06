import pygame
from lib.screen import screen, WIDTH, HEIGHT

class Car:
    def __init__(self, x, y, direction, speed=2):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.turned = False

    def move(self, obstacles):
        if self.can_move(obstacles):
            if not self.turned:
                if self.direction == "right":
                    self.x += self.speed
                    if self.x > WIDTH // 2 - 30:
                        self.turned = True
                        self.direction = "up"
                elif self.direction == "left":
                    self.x -= self.speed
                    if self.x < WIDTH // 2 + 30:
                        self.turned = True
                        self.direction = "down"
            else:
                if self.direction == "up":
                    self.y -= self.speed
                elif self.direction == "down":
                    self.y += self.speed

    def can_move(self, obstacles):
        for car in obstacles:
            if car != self and abs(self.x - car.x) < 25 and abs(self.y - car.y) < 25:
                return False
        return True

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 20, 20))