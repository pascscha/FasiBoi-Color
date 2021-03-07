from IO.core import ControllerValue
import colorsys
import hashlib


class Application:
    DEFAULT_NAME = "BaseApplication"

    def __init__(self, name=None, color=None):
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name

        if color is None:
            hue = int(hashlib.md5(self.name.encode()).hexdigest(), 16) % 255
            self.color = tuple(
                map(lambda x: int(x*255), colorsys.hsv_to_rgb(hue/255, 1, 1)))
        else:
            self.color = color

    def update(self, io, delta):
        raise NotImplementedError("Please implement this method")

    def destroy(self):
        pass
