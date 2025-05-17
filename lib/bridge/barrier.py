import pygame
from lib.screen import screen, scale_to_display

class Barrier:
    """
    Represents a graphical barrier (e.g., a crossing gate) that can open and close
    smoothly over time and be drawn on a Pygame screen.
    """

    def __init__(self, position, angle):
        """
        Initialize the barrier.

        Args:
            position (tuple): The (x, y) position of the barrier's pivot point in logical coordinates.
            angle (float): The angle at which the barrier should be drawn, in degrees.
        """
        self.position = position
        self.width, self.base_height = (2, 50)  # Logical dimensions
        self.height = 0  # Current visible height

        raw = pygame.image.load('assets/barrier.webp').convert_alpha()
        sw, sh = scale_to_display(self.width, self.base_height)
        self.screen_base_w, self.screen_base_h = sw, sh
        self.base_image = pygame.transform.smoothscale(raw, (sw, sh))

        pivot_x, pivot_y = scale_to_display(*self.position)
        self.pivot_px = pygame.math.Vector2(pivot_x, pivot_y)

        self.angle = angle
        self.is_open = True
        self.barrier_open_seconds = 5

    def update(self, delta_time):
        """
        Update the state of the barrier.

        Args:
            delta_time (float): Time elapsed since the last update in seconds.
        """
        self.update_barrier_height(delta_time)

    def update_barrier_height(self, delta_time: float):
        """
        Adjust the barrier's height based on whether it is opening or closing.

        The height is interpolated over time to simulate smooth motion.

        Args:
            delta_time (float): Time since the last update in seconds.
        """
        speed = self.base_height / self.barrier_open_seconds

        if self.is_open:
            self.height = max(0.0, self.height - speed * delta_time)
        else:
            self.height = min(self.base_height, self.height + speed * delta_time)

    def open(self):
        """
        Set the barrier to open. The barrier will begin lowering its visible height.
        """
        self.is_open = True

    def close(self):
        """
        Set the barrier to close. The barrier will begin increasing its visible height.
        """
        self.is_open = False

    def draw(self):
        """
        Draw the barrier onto the screen at its current position, angle, and height.
        """
        frac = max(0.0, min(1.0, self.height / self.base_height))
        crop_h = int(self.screen_base_h * frac)

        cropped = self.base_image.subsurface(
            pygame.Rect(0, 0, self.screen_base_w, crop_h)
        ).copy()

        pivot_surf = pygame.Surface(
            (self.screen_base_w, self.screen_base_h),
            flags=pygame.SRCALPHA
        )

        pivot_surf.blit(cropped, (0, 0))

        rotated = pygame.transform.rotate(pivot_surf, self.angle)
        rect = rotated.get_rect(center=self.pivot_px)
        screen.blit(rotated, rect.topleft)
