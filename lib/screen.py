import pygame
from pygame._sdl2 import Window
import pyautogui

def init_screen():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
    Window.from_display_module().maximize()
    pygame.display.set_caption("Stoplichtsimulator")
    return screen

screen = init_screen()
WIDTH, HEIGHT = screen.get_size()

def update_screen_size():
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = screen.get_size()


def scale_to_display(x, y):
    return int(x / 1920 * WIDTH), int(y / 1080 * HEIGHT)

def scale_to_system(x, y):
    return int(x / WIDTH * 1920), int(y / HEIGHT * 1080)