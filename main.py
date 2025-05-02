import pygame
import yaml
import cProfile
import pstats
import io
import os
from lib.fps_counter import FpsCounter
from lib.messenger import Messenger
from lib.screen import screen, WIDTH, update_screen_size
from lib.simulation import Simulation
import argparse

# Initialize pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Laden en schalen van de achtergronden
background_image = pygame.image.load('assets/background.webp').convert_alpha()
background_orig_width, background_orig_height = background_image.get_size()
scale_factor = WIDTH / background_orig_width
new_height = int(background_orig_height * scale_factor)
background_image = pygame.transform.scale(background_image, (WIDTH, new_height))
overlay_image = pygame.image.load('assets/overlay.webp').convert_alpha()
overlay_image = pygame.transform.scale(overlay_image, (WIDTH, new_height))
fps_counter = FpsCounter()

def load_config(config_dir="config"):
    config = {}
    for filename in os.listdir(config_dir):
        if filename.endswith(".yaml"):
            filepath = os.path.join(config_dir, filename)
            with open(filepath, "r") as file:
                file_config = yaml.safe_load(file)
                config.update(file_config)
    return config

def run_simulation(drukte="rustig"):
    config = load_config()
    messenger = Messenger()
    simulation = Simulation(config, messenger, traffic_level=drukte)
    clock = pygame.time.Clock()
    running = True
    start_time = pygame.time.get_ticks()
    messenger.receive()
    
    # Key press detection variables
    last_b_press_time = 0
    last_e_press_time = 0
    key_cooldown = 500  # Cooldown in milliseconds to prevent multiple spawns
    
    while running:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Manual spawn of vehicles with keyboard
                elif event.key == pygame.K_b and current_time - last_b_press_time > key_cooldown:
                    # Spawn a bus
                    simulation.vehicle_spawner.spawn_priority_vehicle(simulation.vehicles, "bus")
                    last_b_press_time = current_time
                elif event.key == pygame.K_e and current_time - last_e_press_time > key_cooldown:
                    # Spawn a emergency vehicle
                    simulation.vehicle_spawner.spawn_priority_vehicle(simulation.vehicles, "emergency_vehicle")
                    last_e_press_time = current_time
            elif event.type == pygame.VIDEORESIZE:
                update_screen_size()
        
        screen.blit(background_image, (0, 0))
        fps_counter.update()
        simulation.update()
        simulation.draw()
        screen.blit(overlay_image, (0, 0))
        fps_counter.draw()
        messenger.send("tijd", {"simulatie_tijd_ms": elapsed_time})
        pygame.display.flip()
        clock.tick(60)
    
    messenger.stop()
    pygame.quit()

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print("\n❌ Fout:", "De parameter drukte is verplicht.")
        print("👉 Gebruik: python main.py [drukte]")
        print("   waar [drukte] één van de volgende waarden heeft: rustig, spits, stress\n")
        self.print_help()
        exit(2)

if __name__ == '__main__':
    parser = CustomArgumentParser()
    parser.add_argument(
        "drukte",
        choices=["rustig", "spits", "stress"],
    )
    args = parser.parse_args()
    
    # Start de profiler
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Start de simulatie met opgegeven drukte
    run_simulation(drukte=args.drukte)
    
    profiler.disable()
    
    # Print de profiler stats
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    # print(s.getvalue())