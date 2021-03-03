class _BaseDisplay:
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

from IO.display._pygameDisplay import *
from IO.display._cursesDisplay import *