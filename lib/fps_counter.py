import pygame
import time
from lib.screen import screen, scale_to_display, WORLD_WIDTH

class FpsCounter:
    """
    Tracks and displays the current frames per second (FPS) on screen.
    """

    def __init__(self):
        """
        Initialize the FPS counter and font settings.
        """
        self.font = pygame.font.SysFont('Arial', 18, bold=True)
        self.frames = 0
        self.start_time = time.time()
        self.current_fps = 0
        self.update_interval = 0.5  # Interval (in seconds) to recalculate FPS
        self.last_update = self.start_time

    def update(self):
        """
        Increment the frame count and periodically recalculate the FPS.
        """
        self.frames += 1
        current_time = time.time()
        elapsed = current_time - self.last_update

        # Update FPS after each interval
        if elapsed > self.update_interval:
            self.current_fps = self.frames / elapsed
            self.frames = 0
            self.last_update = current_time

    def draw(self):
        """
        Render the FPS value on screen with adaptive scaling and background.
        """
        # Generate the FPS display text
        fps_text = f"FPS: {int(self.current_fps)}"

        # Determine the scale factor based on the resolution
        orig_x, orig_y = 1, 1
        scaled_x, _ = scale_to_display(orig_x, orig_y)
        scale_factor = scaled_x / orig_x

        # Dynamically scale font size
        base_font_size = 16
        scaled_font_size = int(base_font_size * scale_factor)
        scaled_font = pygame.font.Font(None, scaled_font_size)

        # Render text surface
        fps_surface = scaled_font.render(fps_text, True, (255, 255, 0))  # Yellow text
        text_rect = fps_surface.get_rect()

        # Create semi-transparent background
        padding = 20
        bg_padding_x = int(5 * scale_factor)
        bg_padding_y = int(3 * scale_factor)
        background_surface = pygame.Surface((text_rect.width + bg_padding_x * 2, text_rect.height + bg_padding_y * 2))
        background_surface.fill((0, 0, 0))
        background_surface.set_alpha(150)

        # Position in top-right corner with scaled padding
        pos_x, pos_y = scale_to_display(WORLD_WIDTH - padding, padding)
        pos_x -= text_rect.width + bg_padding_x * 2  # Align to right edge

        # Draw background and text to screen
        screen.blit(background_surface, (pos_x - bg_padding_x, pos_y - bg_padding_y))
        screen.blit(fps_surface, (pos_x, pos_y))
