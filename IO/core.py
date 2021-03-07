import time

BUTTON_UP = 0
BUTTON_LEFT = 1
BUTTON_RIGHT = 2
BUTTON_DOWN = 3
BUTTON_A = 4
BUTTON_B = 5
BUTTON_MENU = 6


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
        self.pixels = [[(0, 0, 0) for y in range(self.height)]
                       for x in range(self.width)]
        self.brightness = brightness

    def update(self, x, y, color):
        if x < 0 or x >= self.width:
            raise ValueError("x Coordinates out of bounds!")
        elif y < 0 or y >= self.height:
            raise ValueError("y Coordinates out of bounds!")
        elif min(color) < 0 or max(color) >= 256:
            raise ValueError("Colors have to be between 0 and 255")
        else:
            self.pixels[x][y] = color
            self._update(x, y, tuple(map(lambda x:int(x*self.brightness), color)))

    def _update(self, x, y, color):
        raise NotImplementedError("Please implement this method.")

    def refresh(self):
        pass


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
