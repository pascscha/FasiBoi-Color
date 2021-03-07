import time
from numpy import load
from applications import core
import colorsys


class BeatAnimation(core.Application):
    def __init__(self, npy_path, *args, beats_per_loop=1, duration=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation = load(npy_path)
        self.animation_length = len(self.animation)
        self.beat_frames = self.animation_length / beats_per_loop
        self.duration = duration
        self.last_beat = time.time()
        self.beat_count = 0
        self.hue = 0
        self.last = time.time()

    def update(self, io, delta):
        now = time.time()
        if io.controller.b.get_fresh_value():
            self.beat_count += round((now - self.last) / self.duration)
            self.duration = now - self.last_beat
            self.last_beat = now

        frame = self.animation[int((self.beat_count + (now - self.last_beat) /
                                    self.duration)*self.beat_frames) % self.animation_length]

        self.last = now

        self.hue += delta/2
        self.hue = self.hue % 255
        color = tuple(map(lambda x: int(x*255),
                          colorsys.hsv_to_rgb(self.hue, 1, 1)))

        for x in range(frame.shape[0]):
            for y in range(frame.shape[1]):
                if frame[x][y]:
                    io.display.update(y, x, color)
                else:
                    io.display.update(y, x, (0, 0, 0))
        io.display.refresh()


class AnimationCycler(core.Application):
    def __init__(self, animations, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animations = animations
        self.index = 0

    def update(self, io, delta):
        if io.controller.a.get_fresh_value():
            self.index = (self.index + 1) % len(self.animations)
        self.animations[self.index].update(io, delta)


class SolidColor(core.Application):
    def __init__(self, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.brightness = 0
        self.last = time.time()
        self.up = True

    def update(self, io, delta):
        for x in range(io.display.width):
            for y in range(io.display.height):
                io.display.update(x, y, self.color)
        io.display.refresh()
