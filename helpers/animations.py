"""Helper classes to do some repeated animation tasks
"""

import numpy as np
from IO.color import Color


def blend_colors(color1, color2, prog):
    """If prog=0 it returns color1, if prog=1 color2, otherwise it blends linearly between them according to the given
    prog.
    """
    return Color(*map(lambda c: c[0] * (1 - prog) + c[1] * prog, zip(color1, color2)))


def blend_hsv_colors(color1, color2, prog):
    """If prog=0 it returns color1, if prog=1 color2, otherwise it blends linearly between in HSV space them according to the given
    prog.
    """
    return Color.from_hsv(
        *map(
            lambda c: c[0] * (1 - prog) + c[1] * prog,
            zip(color1.to_hsv(), color2.to_hsv()),
        )
    )

    return Color(*map(lambda c: c[0] * (1 - prog) + c[1] * prog, zip(color1, color2)))

class TimedValue:
    """A value that changes over time"""

    def __init__(self, speed=1):
        self.progression = 0
        self.speed = speed

    def tick(self, delta):
        """Update the value, should be executed every frame"""
        self.progression += delta * self.speed
        return self.progression


class Ticker(TimedValue):
    """Value that ticks in a reglular interval"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, delta):
        """Returns true whenever its progression reaches 1"""
        super().tick(delta)
        if self.progression > 1:
            self.progression -= 1
            return True
        return False


class Blinker(Ticker):
    """Goes back and forth between two values linearly"""

    def __init__(self, value1, value2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value1 = value1
        self.value2 = value2

    @staticmethod
    def blend(value1, value2, prog):
        """If prog=0 it returns value1, if prog=1 value2, otherwise it blends linearly between them according to the
        given prog.
        """
        return value1 * (1 - prog) + value2 * prog

    def tick(self, delta):
        """Returns the current value of the blinker"""
        super().tick(delta)
        prog = 2 * abs(self.progression - 0.5)
        return self.blend(self.value1, self.value2, prog)


class AnimatedValue(TimedValue):
    """A value that changes smoothly over time"""

    def __init__(self, value, speed=1, function=lambda x: x):
        super().__init__(speed)
        self.old_value = value
        self.new_value = value

        self.function = function
        self.progression = 0

    def tick(self, delta):
        """Update the current value and return it"""
        super().tick(delta)
        return self.get_value()

    def set_value(self, value):
        """Set a new value and smoothly transition to that new value"""
        if np.any(value != self.new_value):
            self.old_value = self.get_value()
            self.progression = 0
            self.new_value = value

    def finished(self):
        """Returns true if animation finished"""
        return self.old_value == self.new_value

    @staticmethod
    def blend(value1, value2, prog):
        """If prog=0 it returns value1, if prog=1 value2, otherwise it blends linearly between them according to the
        given prog.
        """
        return value1 * (1 - prog) + value2 * prog

    def get_value(self):
        """Returns the current smoothly animated value"""
        if self.progression >= 1:
            self.old_value = self.new_value
            return self.new_value
        else:
            return self.blend(
                self.old_value, self.new_value, self.function(self.progression)
            )


class AnimatedColor(AnimatedValue):
    """A color that changes smoothly over time"""

    @staticmethod
    def blend(value1, value2, prog):
        """If prog=0 it returns color1, if prog=1 color2, otherwise it blends linearly between them according to the
        given prog.
        """
        return blend_colors(value1, value2, prog)


class AnimatedHSVColor(AnimatedValue):
    """A color that changes smoothly over time"""

    @staticmethod
    def blend(value1, value2, prog):
        """If prog=0 it returns color1, if prog=1 color2, otherwise it blends linearly between them according to the
        given prog.
        """
        return blend_hsv_colors(value1, value2, prog)
