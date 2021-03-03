import pygame
import numpy as np
import random
import time


class Display:
    def __init__(self, width, height, lazy=True):
        self.width = width
        self.height = height
        self.pixels = [[(0, 0, 0) for y in range(self.height)]
                       for x in range(self.width)]
        self.lazy = True

    def update(self, x, y, color):
        if x < 0 or x >= self.width:
            raise ValueError("x Coordinates out of bounds!")
        elif y < 0 or y >= self.height:
            raise ValueError("y Coordinates out of bounds!")
        elif min(color) < 0 or max(color) >= 256:
            raise ValueError("Colors have to be between 0 and 255")
        elif not self.lazy:
            self._update(x, y, tuple(map(int, color)))
        elif color != self.pixels[x][y]:
            self.pixels[x][y] = color
            self._update(x, y, tuple(map(int, color)))

    def _update(self, x, y, color):
        raise NotImplementedError("Please implement this method.")


class PygameDisplay(Display):
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
        pygame.display.update()


class ControllerValue:
    def __init__(self, subscribers=set(), dtype=bool, default=False):
        self.value = default
        self.dtype = dtype
        self.subscribers = subscribers

    def update(self, value):
        new_value = self.dtype(value)
        if new_value != self.value:
            self.value = new_value
            for fun in self.subscribers:
                fun(self.value)

    def subscribe(self, fun):
        self.subscribers.add(fun)

    def unsubscribe(self, fun):
        if fun in self.subscribers:
            self.subscribers.remove(fun)


class BaseController:
    ValueClass = ControllerValue

    def __init__(self):
        self.up = self.ValueClass()
        self.right = self.ValueClass()
        self.down = self.ValueClass()
        self.left = self.ValueClass()
        self.a = self.ValueClass()
        self.b = self.ValueClass()


class PygameController(BaseController):
    def __init__(self):
        super().__init__()
        self.keymap = {
            276: self.left,
            273: self.up,
            275: self.right,
            274: self.down,
            97: self.a,
            98: self.b
        }

    def update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.keymap:
                self.keymap[event.key].update(True)
        elif event.type == pygame.KEYUP:
            if event.key in self.keymap:
                self.keymap[event.key].update(False)


class BeatFeeler:
    def __init__(self, controllerValue):
        controllerValue.subscribe(self.beat)
        self.last = time.time()
        self.duration = 1
        self.beat_count = 0

    def beat(self, on):
        if on:
            now = time.time()
            self.beat_count += round((now - self.last) / self.duration)
            self.duration = now - self.last
            self.last = now

    def getProgression(self):
        now = time.time()
        return self.beat_count + (now - self.last) / self.duration


class BeatAnimation:
    def __init__(self, npy_path, disp, controller):
        self.beatFeeler = BeatFeeler(controller.b)
        self.disp = disp
        self.animation = np.load(npy_path)
        self.animation_length = len(self.animation)
        self.beat_frames = self.animation_length / 2

    def update(self):
        frame = self.animation[int(self.beatFeeler.getProgression(
        )*self.beat_frames) % self.animation_length]

        for x in range(frame.shape[0]):
            for y in range(frame.shape[1]):
                if frame[x][y]:
                    self.disp.update(y,x, (255,255,255))
                else:
                    self.disp.update(y,x, (0,0,0))
                    

if __name__ == "__main__":
    bg_path = "resources/images/bg.png"
    title = "FasiBoi-Color"

    screen_pos = (150, 100)
    screen_size = (200, 300)
    pygame.init()

    try:
        bg_image = pygame.image.load(bg_path)

        win = pygame.display.set_mode(bg_image.get_size())
        pygame.display.set_caption(title)

        disp = PygameDisplay(win, screen_pos, screen_size, 10, 15)
        controller = PygameController()
        beatFeeler = BeatFeeler(controller.b)
        animation = BeatAnimation("resources/animations/shuffle3.npy", disp, controller)

        win.blit(bg_image, (0, 0))

        for x in range(10):
            for y in range(15):
                disp.update(x, y, (random.randint(0, 255),
                                   random.randint(0, 255), random.randint(0, 255)))

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                else:
                    controller.update(event)
            animation.update()

    finally:
        pygame.quit()
