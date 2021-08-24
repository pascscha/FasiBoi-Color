from applications import core


class Paint(core.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_pallette = [
            (0, 0, 0),
            (85, 85, 85),
            (170, 170, 170),
            (255, 255, 255),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (0, 255, 255),
            (255, 0, 255),
            (255, 255, 0)
        ]
        self.pulse_speed = 1.5
        self.selected_index = 3
        self.progression = 0

        self.pixels = self.load_value(
            "pixels", default=[[(0, 0, 0) for _ in range(12)] for _ in range(10)])
        self.cursor = [0, 0]

    def update(self, io, delta):
        if io.controller.b.get_fresh_value():
            self.selected_index = (
                                          self.selected_index + 1) % len(self.color_pallette)
        if io.controller.a.get_fresh_value():
            self.pixels[self.cursor[0]][self.cursor[1]
            ] = self.color_pallette[self.selected_index]
            self.save_value("pixels", self.pixels)

        if io.controller.left.get_fresh_value():
            self.cursor[0] = max(0, self.cursor[0] - 1)
        if io.controller.right.get_fresh_value():
            self.cursor[0] = min(len(self.pixels) - 1, self.cursor[0] + 1)
        if io.controller.up.get_fresh_value():
            self.cursor[1] = max(0, self.cursor[1] - 1)
        if io.controller.down.get_fresh_value():
            self.cursor[1] = min(len(self.pixels[0]) - 1, self.cursor[1] + 1)

        self.progression += delta * self.pulse_speed
        pulser = abs(self.progression - int(self.progression) - 0.5) * 2

        for x in range(len(self.pixels)):
            for y in range(len(self.pixels[x])):
                if [x, y] == self.cursor:
                    color = tuple(map(lambda c: int((255 - c) * (1 - pulser) + c * pulser), self.pixels[x][y]))
                    io.display.update(x, y, color)
                else:
                    io.display.update(x, y, self.pixels[x][y])

        brightness = int(pulser * 255)
        for x in range(io.display.width):
            if x == self.selected_index:
                io.display.update(x, 14, (brightness, brightness, brightness))
            else:
                io.display.update(x, 14, (0, 0, 0))

        for x, color in enumerate(self.color_pallette):
            io.display.update(x, 13, color)
