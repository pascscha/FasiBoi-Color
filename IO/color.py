import numpy as np

class Color(np.ndarray):
    def __new__(cls, r, g, b):
        return np.array([r, g, b], dtype=np.uint8).view(cls)

    @staticmethod
    def convert(color):
        return max(0, min(255, int(color)))

    def __setitem__(self, index, value):
        return super().__setitem__(index, self.convert(value))

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"

    def __add__(self, other):
        return Color(*map(self.convert, super().__add__(other)))

    def __sub__(self, other):
        return Color(*map(self.convert, super().__sub__(other)))

    def __mul__(self, other):
        return Color(*map(self.convert, super().__mul__(other)))

    def __div__(self, other):
        return Color(*map(self.convert, super().__div__(other)))

    @property
    def r(self):
        return self[0]
    
    @property
    def g(self):
        return self[1]

    @property
    def b(self):
        return self[2]

    @r.setter
    def r(self, value):
        self[0] = self.convert(value)
    
    @g.setter
    def g(self, value):
        self[1] = self.convert(value)

    @b.setter
    def b(self, value):
        self[2] = self.convert(value)

def blend(color1, color2, progression):
    return color1  * (1- progression) + color2 * progression

BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
YELLOW = Color(255, 255, 0)
CYAN = Color(0, 255, 255)
MAGENTA = Color(255, 0, 255)