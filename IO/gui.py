import pygame
from IO import core
from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'


class PygameController(core.Controller):
    def __init__(self):
        super().__init__()
        self.keymap = {
            pygame.K_LEFT: self.left,
            pygame.K_UP: self.up,
            pygame.K_RIGHT: self.right,
            pygame.K_DOWN: self.down,
            pygame.K_a: self.a,
            pygame.K_b: self.b,
            pygame.K_ESCAPE: self.menu,
            pygame.K_t: self.teppich
        }

    def update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.keymap:
                self.keymap[event.key].update(True)
        elif event.type == pygame.KEYUP:
            if event.key in self.keymap:
                self.keymap[event.key].update(False)


class PygameDisplay(core.Display):
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

        pygame.draw.rect(
            self.win,
            (0, 0, 0),
            (*screen_pos, *screen_size))

    def _refresh(self):
        pygame.display.update()

    def _update(self, x, y, color):
        left = self.screen_pos[0] + self.pixel_size * x
        top = self.screen_pos[1] + self.pixel_size * y
        pygame.draw.rect(self.win, color, (left, top, self.pixel_size, self.pixel_size))


class PygameIOManager(core.IOManager):
    def __init__(self,
                 bg_path="resources/images/bg.png",
                 title="FasiBoi-Color",
                 screen_pos=(150, 100),
                 screen_size=(200, 300),
                 screen_res=(10, 15)):
        pygame.init()
        pygame.display.set_caption(title)

        if bg_path is not None:
            bg_image = pygame.image.load(bg_path)
            win = pygame.display.set_mode(bg_image.get_size())
            win.blit(bg_image, (0, 0))
        else:
            win = pygame.display.set_mode(screen_size)

        display = PygameDisplay(win, screen_pos, screen_size, *screen_res)
        controller = PygameController()
        super().__init__(controller, display)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            else:
                self.controller.update(event)
        super().update()

    def destroy(self):
        pygame.quit()
