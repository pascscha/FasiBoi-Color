from helpers import animations
import cv2
import numpy as np

from applications import core
from applications.colors import *


class Vector:
    def __init__(self, x, y, speed=1, function=lambda x: x):
        self.speed = speed
        self.function = function
        self._x = animations.AnimatedValue(x, speed=speed, function=function)
        self._y = animations.AnimatedValue(y, speed=speed, function=function)

    @property
    def x(self):
        return self._x.get_value()

    @property
    def y(self):
        return self._y.get_value()

    def tick(self, delta):
        self._x.tick(delta)
        self._y.tick(delta)

    @x.setter
    def x(self, value):
        return self._x.set_value(value)

    @y.setter
    def y(self, value):
        return self._y.set_value(value)

    def __add__(self, other):
        return Vector(
            self.x + other.x, self.y + other.y, speed=self.speed, function=self.function
        )


class DrawableObject:
    def __init__(self, *args, parent=None, offset: Vector = None, smear=0, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent = parent

        if offset is None:
            self._offset = Vector(0, 0)
        else:
            self._offset = offset

        self.smear = 0
        self.last_pos = None

    def offset(self):
        if self.parent is None:
            return self._offset
        else:
            return self.parent.offset() + self._offset

    def tick(self, delta):
        self._offset.tick(delta)

    @staticmethod
    def _empty_canvas(w, h):
        return np.zeros((h, w, 4), dtype=np.uint8)

    def render(self):
        raise NotImplementedError()

    def draw(self, display):
        (x, y), pixels = self.render()
        offset = self.offset()
        x += offset.x
        y += offset.y

        self.last_pos = (x, y)
        x = int(x)
        y = int(y)
        print()
        print("====")
        print(x, y)

        x_range_pix = [0, pixels.shape[0]]
        y_range_pix = [0, pixels.shape[1]]

        x_range_disp = [x, x + pixels.shape[0]]
        y_range_disp = [y, y + pixels.shape[1]]

        if x_range_disp[0] >= display.width or x_range_disp[0] + x_range_disp[1] < 0:
            return

        if y_range_disp[0] >= display.height or y_range_disp[0] + y_range_disp[1] < 0:
            return

        if x_range_disp[0] < 0:
            x_range_pix[0] = -x_range_disp[0]
            x_range_disp[0] = 0

        if y_range_disp[0] < 0:
            y_range_pix[0] = -y_range_disp[0]
            y_range_disp[0] = 0

        if x_range_disp[1] > display.width:
            x_range_pix[1] -= x_range_disp[1] - display.width - 1
            x_range_disp[1] = display.width - 1

        if y_range_disp[1] > display.height:
            y_range_pix[1] -= y_range_disp[1] - display.height - 1
            y_range_disp[1] = display.height - 1

        print(x_range_disp, x_range_pix)
        print(y_range_disp, y_range_pix)
        print(x_range_disp[0], x_range_disp[1], y_range_disp[0], y_range_disp[1])
        print(x_range_pix[0], x_range_pix[1], y_range_pix[0], y_range_pix[1])

        out_pixels = display.pixels[
            x_range_disp[0] : x_range_disp[1], y_range_disp[0] : y_range_disp[1]
        ]
        in_pixels = pixels[
            x_range_pix[0] : x_range_pix[1], y_range_pix[0] : y_range_pix[1]
        ]

        print(in_pixels.shape, out_pixels.shape, display.pixels.shape)

        blend = (in_pixels[:, :, 3].astype(np.float32) / 255).reshape(
            in_pixels.shape[0], in_pixels.shape[1], 1
        )
        print(out_pixels * (1 - blend))
        print(in_pixels[:, :, :3] * blend)
        display.pixels[
            x_range_disp[0] : x_range_disp[1], y_range_disp[0] : y_range_disp[1]
        ] = (out_pixels * (1 - blend) + in_pixels[:, :, :3] * blend).astype(np.uint8)


class Point(DrawableObject):
    def __init__(self, *args, radius=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = radius

    def render(self):
        pix = np.ones(shape=(2 * self.radius, 2 * self.radius, 4)) * 255
        return (-self.radius, -self.radius), pix


class ExampleDrawing(core.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ys = [2, 7, 12]
        self.points = []
        for i, y in enumerate(ys):
            p = Point(
                radius=1,
                offset=Vector(2, y, speed=0.5 + i / 2, function=lambda x: x**2),
            )
            self.points.append(p)

    def update(self, io, delta):
        io.display.fill((0, 0, 0))
        for p in self.points:
            if p._offset.x == 7:
                p._offset.x = 2
            elif p._offset.x == 2:
                p._offset.x = 7
            p.tick(delta)

        for p in self.points:
            p.draw(io.display)
