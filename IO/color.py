"""Defines basic color classes
"""
import colorsys
import numpy as np


class Color(np.ndarray):
    """RGB Color
    """

    def __new__(cls, r, g, b):
        return np.array([r, g, b], dtype=np.uint8).view(cls)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float):
        """
        Creates a color from floating-point hsv values
        Args:
            h: hue
            s: saturation
            v: value

        Returns:
            A RGB color corresponding to the specifed hsv values
        """
        return cls(*map(lambda x: int(x * 255), colorsys.hsv_to_rgb(h, s, v)))

    def to_hsv(self):
        return colorsys.rgb_to_hsv(self.r, self.g, self.b)

    @staticmethod
    def _convert(color):
        return max(0, min(255, int(color)))

    def __setitem__(self, index, value):
        return super().__setitem__(index, self._convert(value))

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"

    def __add__(self, other):
        return Color(*map(self._convert, super().__add__(other)))

    def __sub__(self, other):
        return Color(*map(self._convert, super().__sub__(other)))

    def __mul__(self, other):
        return Color(*map(self._convert, super().__mul__(other)))

    def __div__(self, other):
        return Color(*map(self._convert, super() / other))

    @property
    def r(self):
        """The amount of red in the color
        """
        return self[0]

    @property
    def g(self):
        """The amount of green in the color
        """
        return self[1]

    @property
    def b(self):
        """The amount of blue in the color
        """
        return self[2]

    @r.setter
    def r(self, value):
        self[0] = self._convert(value)

    @g.setter
    def g(self, value):
        self[1] = self._convert(value)

    @b.setter
    def b(self, value):
        self[2] = self._convert(value)


def blend(color1: Color, color2: Color, progression: float):
    """
    Blends two colors linearly according to the progression

    Args:
        color1: The color if the progression is 0
        color2: The color if the progression is 1
        progression: A value from 0 to 1, blending from color1 to color2

    Returns:
        A Color mix from color1 and color2
    """
    return color1 * (1 - progression) + color2 * progression


BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
YELLOW = Color(255, 255, 0)
CYAN = Color(0, 255, 255)
MAGENTA = Color(255, 0, 255)
