def blend_colors(color1, color2, prog):
    return tuple(map(lambda c: c[0] * (1 - prog) + c[1] * prog, zip(color1, color2)))

class AnimatedValue:
    def __init__(self, value, speed=1, function=lambda x:x):
        self.old_value = value
        self.new_value = value

        self.speed = speed
        self.function = function
        self.progression = 0
    
    def tick(self, delta):
        self.progression += delta * self.speed

    def set_value(self, value):
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


