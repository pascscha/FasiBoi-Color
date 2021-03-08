from IO.core import ControllerValue
import colorsys
import hashlib
import os.path
import json

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

        self.save_path = os.path.join("resources", "appdata", self.name.replace(" ", "_")+".json")

    def load_data(self):
        if not os.path.exists(self.save_path):
            return {}
        else:
            with open(self.save_path) as f:
                return json.load(f)

    def save_data(self, data):
        with open(self.save_path, "w+") as f:
            json.dump(data, f)

    def load_value(self, key, default=None):
        data = self.load_data()
        if key in data:
            return data[key]
        else:
            return default

    def save_value(self, key, value):
        data = self.load_data()
        data[key] = value
        self.save_data(data)

    def update(self, io, delta):
        raise NotImplementedError("Please implement this method")

    def destroy(self):
        pass
