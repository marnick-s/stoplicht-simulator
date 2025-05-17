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

# Initialize pygame mixer (for audio) and pygame itself
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Load and scale background and overlay images to fit screen width
def load_and_scale_image(path):
    image = pygame.image.load(path).convert_alpha()
    orig_w, orig_h = image.get_size()
    scale = WIDTH / orig_w
    return pygame.transform.scale(image, (WIDTH, int(orig_h * scale)))

background_image = load_and_scale_image('assets/background.webp')
overlay_image = load_and_scale_image('assets/overlay.webp')
fps_counter = FpsCounter()

# Load all YAML configuration files from the config directory
def load_config(config_dir="config"):
    config = {}
    for filename in os.listdir(config_dir):
        if filename.endswith(".yaml"):
            filepath = os.path.join(config_dir, filename)
            with open(filepath, "r") as file:
                config.update(yaml.safe_load(file) or {})
    return config

# Main simulation runner
def run_simulation(drukte="rustig", silent=False):
    # Silent mode: disable all sound playback
    if silent:
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        pygame.mixer.quit()

    config = load_config()
    messenger = Messenger()
    simulation = Simulation(config, messenger, traffic_level=drukte)
    clock = pygame.time.Clock()
    running = True
    start_time = pygame.time.get_ticks()
    messenger.receive()

    # Keyboard cooldown handling for spawning priority vehicles
    last_press = {'b': 0, 'e': 0}
    cooldown = 500  # milliseconds

    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_b and now - last_press['b'] > cooldown:
                    simulation.vehicle_spawner.spawn_priority_vehicle(simulation.vehicles, "bus")
                    last_press['b'] = now
                elif event.key == pygame.K_e and now - last_press['e'] > cooldown:
                    simulation.vehicle_spawner.spawn_priority_vehicle(simulation.vehicles, "emergency_vehicle")
                    last_press['e'] = now
            elif event.type == pygame.VIDEORESIZE:
                update_screen_size()

        # Draw everything to the screen
        screen.blit(background_image, (0, 0))
        fps_counter.update()
        simulation.update()
        simulation.draw()
        screen.blit(overlay_image, (0, 0))
        fps_counter.draw()
        messenger.send("tijd", {"simulatie_tijd_ms": now})
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    # Clean up on exit
    messenger.stop()
    pygame.quit()

# Custom argument parser for better error messages
class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"\n❌ Fout: {message}")
        print("Gebruik: python main.py [drukte] [--stil]")
        print("drukte: rustig, spits, stress; --stil: geen geluid")
        super().print_help()
        exit(2)

# Entry point of the script
if __name__ == '__main__':
    parser = CustomArgumentParser()
    parser.add_argument(
        "drukte",
        choices=["rustig", "spits", "stress"],
        help="Verkeersintensiteit"
    )
    parser.add_argument(
        "-s", "--stil",
        action='store_true',
        help='Start de simulatie zonder geluid'
    )
    args = parser.parse_args()

    # Optional profiling of the simulation performance
    profiler = cProfile.Profile()
    profiler.enable()

    run_simulation(drukte=args.drukte, silent=args.stil)

    profiler.disable()
    s = io.StringIO()
    pstats.Stats(profiler, stream=s).sort_stats('cumulative').print_stats()
    # Uncomment the next line to print the profiling output
    # print(s.getvalue())
