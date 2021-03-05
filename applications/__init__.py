from IO.controller import ControllerValue

def controllerInput(func):
    def inner(self, button, value):
        if self.running:
            if self.active:
                func(self, button, value)
        else:
            button.unsubscribe(func)
    return inner


class _BaseApplication:
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

    @controllerInput
    def close(self, button, value):
        if value:
            self.running = False
            self.destroy()

    def update(self):
        pass

    def destroy(self):
        pass

        
from applications.menus import *