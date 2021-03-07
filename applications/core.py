from IO.core import ControllerValue

class Application:
    DEFAULT_NAME = "BaseApplication"

    def __init__(self, name=None):
        if name is None:
            self.name = self.DEFAULT_NAME
        else:
            self.name = name
        
    def update(self, io, delta):
        raise NotImplementedError("Please implement this method")

    def destroy(self):
        pass