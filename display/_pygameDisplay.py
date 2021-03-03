from display import _BaseDisplay
import pygame.draw

class PygameDisplay(_BaseDisplay):
    def __init__(self, win, screen_pos, screen_size, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.win = win

        max_px_width = screen_size[0] // self.width
        max_px_height = screen_size[1] // self.height
        self.pixel_size = min(max_px_width, max_px_height)

        # Recenter screen
        new_pos_x = screen_pos[0] + \
            (screen_size[0] - self.pixel_size * self.width) // 2
        new_pos_y = screen_pos[1] + \
            (screen_size[1] - self.pixel_size * self.height) // 2
        self.screen_pos = (new_pos_x, new_pos_y)

    def _update(self, x, y, color):
        left = self.screen_pos[0] + self.pixel_size * x
        top = self.screen_pos[1] + self.pixel_size * y
        pygame.draw.rect(self.win, color, (left, top,
                                           self.pixel_size, self.pixel_size))
