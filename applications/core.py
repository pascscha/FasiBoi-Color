import colorsys
import hashlib
import os.path
import json


class Application:

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

        self.save_path = os.path.join(
            "resources", "appdata", self.name.replace(" ", "_")+".json")

    def load_data(self):
        """Loads application data from disk. The filename is automatically generated based on the application name.

        Returns:
            json: Either an empty json object if no data has been stored yet or the stored application data.
        """
        if not os.path.exists(self.save_path):
            return {}
        else:
            with open(self.save_path) as f:
                return json.load(f)

    def save_data(self, data):
        """Stores application data to disk. The filename is automatically generated based on the application name.

        Args:
            data (dict): The data that we want to store
        """
        with open(self.save_path, "w+") as f:
            json.dump(data, f)

    def load_value(self, key, default=None):
        """Loads single value from application data on disk

        Args:
            key (str): The name of the value we want to load
            default (*, optional): The return value if this value has not been stored to disk yet.
            Defaults to None.

        Returns:
            *: The value if it exists, else the default value
        """
        data = self.load_data()
        if key in data:
            return data[key]
        else:
            return default

    def save_value(self, key, value):
        """Stores single value to disk

        Args:
            key (str): The name of the value we want to store
            value (*): The value we want to store
        """
        data = self.load_data()
        data[key] = value
        self.save_data(data)

    def update(self, io, delta):
        """Updates Application to advance 1 frame

        Args:
            io (IO.core.IOManager): The IO manager that the application is running in
            delta (float): How much time has passed since the last frame

        Raises:
            NotImplementedError: If the method is not implemented by the derived classes.
        """
        raise NotImplementedError("Please implement this method")

    def destroy(self):
        """Closes application
        """
        pass
