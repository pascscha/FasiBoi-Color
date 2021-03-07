from IO.core import ControllerValue

def controllerInput(func):
    def inner(self, button, value):
        if self.running:
            if self.active:
                func(self, value)
        else:
            button.unsubscribe(func)
    return inner


class Application:
    DEFAULT_NAME = "BaseApplication"

    def __init__(self, io, name=None):
        self.io = io
        self.io.controller.menu.subscribe(self.close)

        self.running = True
        self.active = True

        if name is None:
            self.name = self.DEFAULT_NAME
        else:
            self.name = name

    def __enter__(self):
        return self
    
    def __exit__(self, *args, **keargs):
        self.destroy()
        
    @controllerInput
    def close(self, value):
        if value:
            self.running = False
            self.destroy()

    def update(self):
        pass

    def destroy(self):
        pass