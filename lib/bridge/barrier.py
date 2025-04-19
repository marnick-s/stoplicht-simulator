import pygame
from lib.screen import screen, scale_to_display

class Barrier():
    def __init__(self, position, angle):
        self.position = position
        self.width, self.base_height = (2, 50)
        self.height = 0

        raw = pygame.image.load('assets/barrier.webp').convert_alpha()
        sw, sh = scale_to_display(self.width, self.base_height)
        self.screen_base_w, self.screen_base_h = sw, sh
        self.base_image = pygame.transform.smoothscale(raw, (sw, sh))

        pivot_x, pivot_y = scale_to_display(*self.position)
        self.pivot_px = pygame.math.Vector2(pivot_x, pivot_y)

        self.angle = angle
        self.is_open = True
        self.barrier_open_seconds = 5


    def update(self):
        self.update_barrier_height()


    def update_barrier_height(self):
        change_per_frame = self.base_height / (self.barrier_open_seconds * 30)

        # Slagboom is aan het openen
        if (self.is_open and self.height > 0):
            self.height -= change_per_frame

        # Slagboom is aan het sluiten
        if ((not self.is_open) and self.height < self.base_height):
            self.height += change_per_frame


    def open(self):
        self.is_open = True


    def close(self):
        self.is_open = False


    def draw(self):
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
        rect    = rotated.get_rect(center=self.pivot_px)
        screen.blit(rotated, rect.topleft)
