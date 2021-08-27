from applications import core, menu
from IO import effects
from helpers import textutils, bitmaputils


class Slider(core.Application):
    def __init__(self, *args, start=0, end=1, steps=10, default=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end
        self.steps = steps

        default = self.load_value("default", default=default)
        self.value_index = int(steps * (default - start) / (end - start))
        self.delta = (end - start) / steps

    def update(self, io, delta):
        if io.controller.button_up.fresh_press():
            self.value_index += 1
            self.value_index = min(self.steps, self.value_index)
        if io.controller.button_down.fresh_press():
            self.value_index -= 1
            self.value_index = max(0, self.value_index)

        self.save_value("default", self.get_value())
        for x in range(0, io.display.width):
            for y in range(io.display.height):
                io.display.update(x, y, (0, 0, 0))

        for x in range(int(io.display.width / 3),
                       int(2 * io.display.width / 3) + 1):
            for y in range(int((1 - self.value_index / self.steps)
                           * io.display.height), io.display.height):
                io.display.update(x, y, self.color)

    def get_value(self):
        return self.start + self.value_index * self.delta


class NumberChoice(core.Application):
    def __init__(
            self,
            *args,
            start=1,
            end=100,
            step_size=1,
            default=50,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.end = end
        self.step_size = step_size
        default = self.load_value("default", default=default)
        self.value = min(end, max(start, default))

    def update(self, io, delta):
        if io.controller.button_up.fresh_press():
            self.value += self.step_size
            self.value = min(self.end, self.value)
        if io.controller.button_down.fresh_press():
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

        bmp = textutils.get_text_bitmap(str(self.value))
        bitmaputils.apply_bitmap(
            bmp,
            io.display,
            (io.display.width // 2 - bmp.shape[1] // 2,
             io.display.height // 2 - bmp.shape[0] // 2),
            fg_color=self.color)


class BrightnessSlider(Slider):
    def update(self, io, delta):
        super().update(io, delta)
        io.display.brightness = self.get_value()


class FPSChoice(NumberChoice):
    def update(self, io, delta):
        super().update(io, delta)
        io.fps = self.value

class ColorPaletteApplyer:
    def __init__(self, parent, palette_name):
        self.parent = parent
        self.palette_name = palette_name

    def __call__(self, io):
        self.parent.palette_name = self.palette_name

class ColorPaletteChoice(core.Application):
    PALETTES = {
        "GB": effects.ColorPalette(colors=[
            (0x9b, 0xbc, 0x0f),
            (0x8b, 0xac, 0x0f),
            (0x30, 0x62, 0x30),
            (0x0f, 0x38, 0x0f)
        ]),
        "G2": effects.ColorPalette(colors=[
            (0x88, 0xc0, 0x70),
            (0x08, 0x18, 0x20),
            (0x34, 0x68, 0x56),
            (0xe0, 0xf8, 0xd0)
        ]),
        "BY": effects.ColorPalette(colors=[
            (0xab, 0x46, 0x46),
            (0x16, 0x16, 0x16),
            (0x8f, 0x9b, 0xf6),
            (0xf0, 0xf0, 0xf0)
        ]),
        "GR": effects.ColorPalette(colors=[
            (255,255,255),
            (85,85,85),
            (170,170,170),
            (0,0,0)
        ])
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.palette_name = None
        choices = [menu.Choice("Default", (255, 255, 255), ColorPaletteApplyer(self, None))] + \
                  [menu.Choice(name, (255, 255, 255), ColorPaletteApplyer(self, name)) for name, palette in self.PALETTES.items()]
        self.chooser = menu.SlidingChoice(choices, 5)

    def update(self, io, delta):
        io.display.fill((0, 0, 0))
        self.chooser.update(io, delta)
        if self.palette_name in self.PALETTES:
            io.color_palette = self.PALETTES[self.palette_name]
        else:
            io.color_palette = None

        if self.chooser.prog == int(self.chooser.prog):
            choice = self.chooser.choices[int(self.chooser.prog)]
            if choice.fun.palette_name in self.PALETTES:
                palette = self.PALETTES[choice.fun.palette_name]
                colors = palette.colors
                n_colors = len(colors)
                n_displayed = min(n_colors, io.display.width)
                left = (io.display.width - n_displayed)//2
                for i, x in enumerate(range(left, left + n_displayed)):
                    io.display.update(x, 12, colors[i])

    