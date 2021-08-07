import numpy as np

def blend_colors(color1, color2, prog):
    return tuple(map(lambda c: c[0] * (1 - prog) + c[1] * prog, zip(color1, color2)))

class TimedValue:
    def __init__(self, speed=1):
        self.progression = 0
        self.speed = speed

    def tick(self, delta):
        self.progression += delta * self.speed
        return self.progression

class Ticker(TimedValue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tick(self, delta):
        super().tick(delta)
        if self.progression > 1:
            self.progression -= 1
            return True
        return False

class Blinker(Ticker):
    def __init__(self, value1, value2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value1 = value1
        self.value2 = value2
    
    @staticmethod
    def blend(value1, value2, prog):
        return value1 * (1 - prog) + value2 * prog

    def tick(self, delta):
        super().tick(delta)
        prog = 2*abs(self.progression - 0.5)
        return self.blend(self.value1, self.value2, prog)

class AnimatedValue(TimedValue):
    def __init__(self, value, speed=1, function=lambda x:x):
        self.old_value = value
        self.new_value = value

        self.speed = speed
        self.function = function
        self.progression = 0
    
    def tick(self, delta):
        self.progression += delta * self.speed
        return self.get_value()

    def set_value(self, value):
        if np.any(value != self.new_value):
            self.old_value = self.get_value()
            self.progression = 0
            self.new_value = value

    @staticmethod
    def blend(value1, value2, prog):
        return self.old_value * (1 - prog) + self.new_value * prog

    def get_value(self):
        if self.progression >= 1:
            self.old_value = self.new_value
            return self.new_value
        else:
            return self.blend(self.old_value, self.new_value, self.function(self.progression))

class AnimatedColor(AnimatedValue):
    @staticmethod
    def blend(value1, value2, prog):
        return blend_colors(value1, value2, prog)