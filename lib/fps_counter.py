import pygame
import time
from lib.screen import screen, scale_to_display, WORLD_WIDTH

class FpsCounter:
    def __init__(self):
        self.font = pygame.font.SysFont('Arial', 18, bold=True)
        self.frames = 0
        self.start_time = time.time()
        self.current_fps = 0
        self.update_interval = 0.5  # Update FPS calculation every 0.5 seconds
        self.last_update = self.start_time
        
    def update(self):
        self.frames += 1
        current_time = time.time()
        elapsed = current_time - self.last_update
        
        # Update FPS calculation every update_interval seconds
        if elapsed > self.update_interval:
            self.current_fps = self.frames / elapsed
            self.frames = 0
            self.last_update = current_time
    
    def draw(self):
        # Create FPS text
        fps_text = f"FPS: {int(self.current_fps)}"
        
        # Get the scaling factor by calculating the ratio between actual and original resolution
        # We'll get this by using scale_to_display on a known size
        orig_x, orig_y = 1, 1
        scaled_x, scaled_y = scale_to_display(orig_x, orig_y)
        scale_factor = scaled_x / orig_x  # This gives us the scaling ratio
        
        # Scale font size using the same scale factor
        base_font_size = 16  # Adjust this to your preferred base font size
        scaled_font_size = int(base_font_size * scale_factor)
        scaled_font = pygame.font.Font(None, scaled_font_size)
        
        fps_surface = scaled_font.render(fps_text, True, (255, 255, 0))  # Yellow text
    
        # Add a semi-transparent black background
        text_rect = fps_surface.get_rect()
        
        # Scale padding
        padding = 20
        scaled_padding = int(padding * scale_factor)
        bg_padding_x = int(5 * scale_factor)
        bg_padding_y = int(3 * scale_factor)
        
        # Create background with scaled dimensions
        background_surface = pygame.Surface((text_rect.width + bg_padding_x*2, text_rect.height + bg_padding_y*2))
        background_surface.fill((0, 0, 0))
        background_surface.set_alpha(150)
        
        # Position in top-right corner with padding (scaled)
        pos_x, pos_y = scale_to_display(WORLD_WIDTH - padding, padding)
    
        # Adjust for text size to align properly
        pos_x -= text_rect.width + bg_padding_x*2
    
        # Draw on screen
        screen.blit(background_surface, (pos_x - bg_padding_x, pos_y - bg_padding_y))
        screen.blit(fps_surface, (pos_x, pos_y))