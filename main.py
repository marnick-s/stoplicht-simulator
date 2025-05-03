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

# Initialize pygame mixer and pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Laden en schalen van de achtergronden
def load_and_scale_image(path):
    image = pygame.image.load(path).convert_alpha()
    orig_w, orig_h = image.get_size()
    scale = WIDTH / orig_w
    return pygame.transform.scale(image, (WIDTH, int(orig_h * scale)))

background_image = load_and_scale_image('assets/background.webp')
overlay_image = load_and_scale_image('assets/overlay.webp')
fps_counter = FpsCounter()

def load_config(config_dir="config"):
    config = {}
    for filename in os.listdir(config_dir):
        if filename.endswith(".yaml"):
            filepath = os.path.join(config_dir, filename)
            with open(filepath, "r") as file:
                config.update(yaml.safe_load(file) or {})
    return config

def run_simulation(drukte="rustig", silent=False):
    # Stilte optie: disable mixer
    if silent:
        # Stop en sluit alle geluidssystemen af
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

    # Key press cooldown
    last_press = {'b': 0, 'e': 0}
    cooldown = 500

    while running:
        now = pygame.time.get_ticks()
        elapsed = now - start_time

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

        screen.blit(background_image, (0, 0))
        fps_counter.update()
        simulation.update()
        simulation.draw()
        screen.blit(overlay_image, (0, 0))
        fps_counter.draw()
        messenger.send("tijd", {"simulatie_tijd_ms": elapsed})
        pygame.display.flip()
        clock.tick(60)

    messenger.stop()
    pygame.quit()

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"\n❌ Fout: {message}")
        print("Gebruik: python main.py [drukte] [--stil]")
        print("drukte: rustig, spits, stress; --stil: geen geluid")
        super().print_help()
        exit(2)

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

    profiler = cProfile.Profile()
    profiler.enable()

    run_simulation(drukte=args.drukte, silent=args.stil)

    profiler.disable()
    s = io.StringIO()
    pstats.Stats(profiler, stream=s).sort_stats('cumulative').print_stats()
    # print(s.getvalue())
