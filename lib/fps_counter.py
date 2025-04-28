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
        fps_surface = self.font.render(fps_text, True, (255, 255, 0))  # Yellow text
        
        # Add a semi-transparent black background for better visibility
        text_rect = fps_surface.get_rect()
        background_surface = pygame.Surface((text_rect.width + 10, text_rect.height + 6))
        background_surface.fill((0, 0, 0))
        background_surface.set_alpha(150)

        # Position in top-right corner with padding
        padding = 20
        pos_x, pos_y = scale_to_display(WORLD_WIDTH - padding, padding)
        
        # Adjust for text size to align properly
        pos_x -= text_rect.width + 10
        
        # Draw on screen
        screen.blit(background_surface, (pos_x - 5, pos_y - 3))
        screen.blit(fps_surface, (pos_x, pos_y))