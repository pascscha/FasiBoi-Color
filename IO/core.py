class ControllerValue:
    def __init__(self, subscribers=[], dtype=bool, default=False):
        self.value = default
        self.dtype = dtype
        self.subscribers = set(subscribers)

    def update(self, value):
        new_value = self.dtype(value)
        if new_value != self.value:
            self.value = new_value
            for fun in self.subscribers:
                fun(self, self.value)

    def subscribe(self, fun):
        self.subscribers.add(fun)

    def unsubscribe(self, fun):
        if fun in self.subscribers:
            self.subscribers.remove(fun)


class Controller:
    ValueClass = ControllerValue

    def __init__(self):
        self.up = self.ValueClass()
        self.right = self.ValueClass()
        self.down = self.ValueClass()
        self.left = self.ValueClass()
        self.a = self.ValueClass()
        self.b = self.ValueClass()
        self.menu = self.ValueClass()


class Display:
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

    def refresh(self):
        pass

class IOManager:
    def __init__(self, controller, display):
        self.controller = controller
        self.display = display
        self.running = True

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.destroy()

    def update(self):
        raise NotImplementedError("Please implement this method.")

    def destroy(self):
        pass

