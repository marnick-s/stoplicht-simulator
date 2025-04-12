import time
import pygame
import yaml
import cProfile
import pstats
import io
from lib.messenger import Messenger
from lib.screen import screen, WIDTH, HEIGHT, update_screen_size
from lib.simulation import Simulation

# Laden en schalen van de achtergronden
background_image = pygame.image.load('assets/background.webp').convert_alpha()
background_orig_width, background_orig_height = background_image.get_size()
scale_factor = WIDTH / background_orig_width
new_height = int(background_orig_height * scale_factor)
background_image = pygame.transform.scale(background_image, (WIDTH, new_height)) 

overlay_image = pygame.image.load('assets/overlay.webp').convert_alpha()
overlay_image = pygame.transform.scale(overlay_image, (WIDTH, new_height))

def load_config(filename="simulation.yaml"):
    with open(filename, "r") as file:
        return yaml.safe_load(file)

def run_simulation():
    config = load_config()
    messenger = Messenger()
    simulation = Simulation(config, messenger)

    clock = pygame.time.Clock()
    running = True
    start_time = pygame.time.get_ticks()

    messenger.receive()

    while running:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time

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
        screen.blit(overlay_image, (0, 0))

        messenger.send("tijd", {"simulatie_tijd_ms": elapsed_time})

        pygame.display.flip()
        clock.tick(30)

    messenger.stop()
    pygame.quit()

if __name__ == '__main__':
    # Zet de profiler op
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Start de simulatie (dit is jouw 'everything draaien')
    run_simulation()
    
    profiler.disable()

    # Resultaten verzamelen en sorteren
    s = io.StringIO()
    sortby = 'cumulative'  # Je kunt ook 'time' proberen
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    
    # Resultaten printen in de console
    print(s.getvalue())
