import colorsys
import hashlib
import os.path
import json
import time
import threading


class Waker:
    def wake_up(self):
        raise NotImplementedError("Please implement this method")


class TimeWaker(Waker):
    def __init__(self, duration):
        self.end = time.time() + duration

    def wake_up(self):
        return time.time() >= self.end


class ButtonPressWaker(Waker):
    def __init__(self, button):
        self.button = button

    def wake_up(self):
        return self.button._value and self.button.fresh


class ButtonReleaseWaker(Waker):
    def __init__(self, button):
        self.button = button

    def wake_up(self):
        return (not self.button._value) and self.button.fresh


class LambdaWaker(Waker):
    def __init__(self, wakeup_fun):
        self.wakeup_fun = wakeup_fun

    def wake_up(self):
        return self.wakeup_fun()


class Application:
    MAX_FPS = None

    def __init__(self, name=None, color=None):
        if name is None:
            self.name = self.__class__.__name__
        else:
            self.name = name

        if color is None:
            hue = int(hashlib.md5(self.name.encode()).hexdigest(), 16) % 255
            self.color = tuple(
                map(lambda x: int(x * 255), colorsys.hsv_to_rgb(hue / 255, 1, 1))
            )
        else:
            self.color = color

        self.wakers = None
        self.sleep_time = 0

        self.save_path = os.path.join(
            "resources", "appdata", self.name.replace(" ", "_") + ".json"
        )

    def load_data(self):
        """Loads application data from disk. The filename is automatically generated based on the application name.

        Returns:
            json: Either an empty json object if no data has been stored yet or the stored application data.
        """
        if not os.path.exists(self.save_path):
            return {}
        else:
            try:
                with open(self.save_path) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}

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

    def sleep(self, wakers):
        """Skips update until given condition is met

        Args:
            wakers (function): Function returning a boolean, deciding when to continue.
        """
        self.sleep_time = 0
        self.wakers = wakers

    def wake_up(self):
        """Wakes application up, ensuring it does not sleep the next frame"""
        self.wakers = None

    def is_sleeping(self, delta):
        """Checks wether the application is sleeping

        Returns:
            bool: True if the application does not need to update
        """
        if self.wakers is None or len(self.wakers) == 0:
            return False
        else:
            if any(waker.wake_up() for waker in self.wakers):
                self.wakers = None
                return False
            else:
                self.sleep_time += delta
                return True

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
        """Closes application"""
        self.wakers = None
        self.sleep_time = 0
