from applications import core
from helpers import textutils, bitmaputils
import colorsys
import hashlib


class Slider(core.Application):
    def __init__(self, *args, start=0, end=1, steps=10, default=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end
        self.steps = steps

        default = self.load_value("default", default=default)
        self.value_index = int(steps * (default - start) / (end - start))
        self.delta = (end - start)/steps

    def update(self, io, delta):
        if io.controller.up.get_fresh_value():
            self.value_index += 1
            self.value_index = min(self.steps, self.value_index)
        if io.controller.down.get_fresh_value():
            self.value_index -= 1
            self.value_index = max(0, self.value_index)

        self.save_value("default", self.get_value())
        for x in range(0, io.display.width):
            for y in range(io.display.height):
                io.display.update(x, y, (0, 0, 0))

        for x in range(int(io.display.width/3), int(2*io.display.width/3)+1):
            for y in range(int((1-self.value_index/self.steps)*io.display.height), io.display.height):
                io.display.update(x, y, self.color)

    def get_value(self):
        return self.start + self.value_index * self.delta


class NumberChoice(core.Application):
    def __init__(self, *args, start=1, end=100, step_size=1, default=50, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end
        self.step_size = step_size
        default = self.load_value("default", default=default)
        self.value = min(end, max(start, default))

    def update(self, io, delta):
        if io.controller.up.get_fresh_value():
            self.value += self.step_size
            self.value = min(self.end, self.value)
        if io.controller.down.get_fresh_value():
            self.value -= self.step_size
            self.value = max(self.start, self.value)

        self.save_value("default", self.value)

        for x in range(io.display.width):
            for y in range(io.display.height):
                if y == 0 or y == io.display.height - 1:
                    color = self.color
                else:
                    color = (0, 0, 0)
                io.display.update(x, y, color)

        bmp = textutils.getTextBitmap(str(self.value))
        bitmaputils.applyBitmap(
            bmp,
            io.display,
            (io.display.width//2-bmp.shape[1]//2,
             io.display.height//2-bmp.shape[0]//2),
            color0=(0, 0, 0),
            color1=self.color)


class BrightnessSlider(Slider):
    def update(self, io, delta):
        super().update(io, delta)
        io.display.brightness = self.get_value()

class FPSChoice(NumberChoice):
    def update(self, io, delta):
        super().update(io, delta)
        io.fps = self.value
