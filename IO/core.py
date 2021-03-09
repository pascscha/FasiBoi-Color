import time
import numpy as np

class ControllerValue:
    def __init__(self,  dtype=bool, default=False):
        self._value = default
        self.fresh = True
        self.dtype = dtype

    def update(self, value):
        new_value = self.dtype(value)
        if new_value != self._value:
            self._value = new_value
            self.fresh = True

    def get_value(self):
        self.fresh = False
        return self._value

    def get_fresh_value(self):
        if self.fresh:
            self.fresh = False
            return self._value
        else:
            return None

class Controller:
    ValueClass = ControllerValue

    def __init__(self):
        self.up = ControllerValue()
        self.right = ControllerValue()
        self.down = ControllerValue()
        self.left = ControllerValue()
        self.a = ControllerValue()
        self.b = ControllerValue()
        self.menu = ControllerValue()


class Display:
    def __init__(self, width, height, brightness=1, lazy=True):
        self.width = width
        self.height = height
        self.pixels = np.zeros((width, height, 3), dtype=np.uint8)
        self.last_pixels = np.ones((width, height, 3), dtype=np.uint8)
        self.brightness = brightness

    def checkCoordinates(self, x, y):
        if x < 0 or x >= self.width:
            raise ValueError("x Coordinates out of bounds!")
        elif y < 0 or y >= self.height:
            raise ValueError("y Coordinates out of bounds!")

    def checkColor(self, color):
        if min(color) < 0 or max(color) >= 256:
            raise ValueError("Colors have to be between 0 and 255")

    def update(self, x, y, color):
        self.checkCoordinates(x, y)
        self.checkColor(color)
        color = tuple(map(lambda x: int(x*self.brightness), color))
        self.pixels[x][y] = color

    def fill(self, color):
        self.checkColor(color)
        self.pixels = np.ones((self.width, self.height, 3), dtype=np.uint8) * color * self.brightness

    def _update(self, x, y, color):
        raise NotImplementedError("Please implement this method!")

    def _refresh(self):
        pass

    def refresh(self):
        # Only update pixels that have changed
        for x,y in zip(*np.where(np.any(self.pixels != self.last_pixels,axis=2))):
            self._update(x, y, self.pixels[x][y])
        self.last_pixels = self.pixels.copy()
        self._refresh()

class IOManager:
    def __init__(self, controller, display, fps=30):
        self.controller = controller
        self.display = display
        self.running = True
        self.applications = None
        self.fps = fps

    def run(self, application):
        self.applications = [application]
        last = time.time()
        delta = 0
        while len(self.applications) > 0:
            now = time.time()
            delta = now - last
            last = now
            self.update()
            self.applications[-1].update(self, delta)
            self.display.refresh()
            if self.controller.menu.get_fresh_value():
                self.closeApplication()
            sleep = max(0, min(delta, 1/self.fps))
            time.sleep(max(0, min(delta, 1/self.fps)))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.running = False
        while len(self.applications) > 0:
            self.closeApplication()
        self.destroy()

    def openApplication(self, application):
        self.applications.append(application)

    def closeApplication(self):
        if len(self.applications) > 0:
            self.applications[-1].destroy()
            self.applications = self.applications[:-1]
        if len(self.applications) == 0:
            self.running = False

    def update(self):
        pass

    def destroy(self):
        pass
