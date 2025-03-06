import pygame
import yaml
from lib.screen import screen, WIDTH, HEIGHT, update_screen_size
from lib.simulation import Simulation

background_image = pygame.image.load('assets/background.png')
orig_width, orig_height = background_image.get_size()
new_height = int(WIDTH * orig_height / orig_width)
background_image = pygame.transform.scale(background_image, (WIDTH, new_height))

def load_config(filename="simulation.yaml"):
    with open(filename, "r") as file:
        return yaml.safe_load(file)

config = load_config()
simulation = Simulation(config)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            update_screen_size()

    screen.blit(background_image, (0, 0))
    simulation.update()
    simulation.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
