from IO.controller import ControllerValue

class _BaseApplication:
    def __init__(self, io):
        self.io = io
        self.io.controller.menu.subscribe(self.close)

    def update(self):
        pass

    def close(self, *args, **kwargs):
        self.destroy()

    def destroy(self):
        for val in filter(lambda val:isinstance(val, ControllerValue), self.io.controller.__dict__.values()):
            # Make sure none of our functions listen to the controller anymore.
            for fun in list(val.subscribers):
                if fun.__self__ == self:
                    val.unsubscribe(fun)