import time
import numpy as np


class ControllerValue:
    def __init__(self,  dtype=bool, default=False):
        self._value = default
        self.fresh = True
        self.dtype = dtype

    def update(self, value):
        """Assigns a new value to the button/input

        Args:
            value (self.dtype): The new value that is assigned to that button
        """
        new_value = self.dtype(value)
        if new_value != self._value:
            self._value = new_value
            self.fresh = True

    def get_value(self):
        """Gets the current value of the button/input

        Returns:
            self.dtype: The current Value of the controller
        """
        self.fresh = False
        return self._value

    def get_fresh_value(self):
        """Gets the current value of that button/input, if it has not been accessed yet (if it's fresh).
        Otherwise returns None

        Returns:
            self.dtype: The value of the button/input if it has not been accessed yet, otherwise None
        """
        if self.fresh:
            self.fresh = False
            return self._value
        else:
            return None


class Controller:

    def __init__(self):
        self.up = ControllerValue()
        self.right = ControllerValue()
        self.down = ControllerValue()
        self.left = ControllerValue()
        self.a = ControllerValue()
        self.b = ControllerValue()
        self.menu = ControllerValue()


class Display:
    def __init__(self, width, height, brightness=1):
        self.width = width
        self.height = height
        self.pixels = np.zeros((width, height, 3), dtype=np.uint8)
        self.last_pixels = np.ones((width, height, 3), dtype=np.uint8)
        self.brightness = brightness

    def checkCoordinates(self, x, y):
        """Checks wether the given coordinates are valid

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Raises:
            ValueError: If X or Y coordinates are out of bounds
        """
        if x < 0 or x >= self.width:
            raise ValueError("x Coordinates out of bounds!")
        elif y < 0 or y >= self.height:
            raise ValueError("y Coordinates out of bounds!")

    def checkColor(self, color):
        """Checks wether a color is valid

        Args:
            color ((int, int, int)): The color

        Raises:
            ValueError: If the color is not properly formatted
        """
        if min(color) < 0 or max(color) >= 256:
            raise ValueError("Colors have to be between 0 and 255")
        elif len(color) != 3:
            raise ValueError("Colors must have 3 channels")

    def update(self, x, y, color):
        """Updates single pixel on the screen

        Args:
            x (int): The x coordinate of that pixel
            y (int): The y coordinate of that pixel
            color ((int, int, int)): The new rgb color of that pixel
        """
        self.checkCoordinates(x, y)
        self.checkColor(color)
        color = tuple(map(lambda x: int(x*self.brightness), color))
        self.pixels[x][y] = color

    def fill(self, color):
        """Fills the entire screen with one color

        Args:
            color ((int, int, int)): The rgb color to fill the screen with
        """
        self.checkColor(color)
        self.pixels = np.ones((self.width, self.height, 3),
                              dtype=np.uint8) * color * self.brightness

    def _update(self, x, y, color):
        raise NotImplementedError("Please implement this method!")

    def _refresh(self):
        pass

    def refresh(self):
        """Shows changes on the screen. Only updated pixels that have been changed
        since last call to this function.
        """
        # Only update pixels that have changed
        for x, y in zip(*np.where(np.any(self.pixels != self.last_pixels, axis=2))):
            self._update(x, y, self.pixels[x][y])
        self.last_pixels = self.pixels.copy()
        self._refresh()

class WindowAnimation:
    def __init__(self, display, duration):
        self.duration = duration
        self.start_pixels = display.pixels
        self.start_time = time.time()

    def is_finished(self):
        return time.time() >= self.start_time + self.duration

    def apply(self, display):
        raise NotImplementedError("Please Implement this method")

class SlideDown(WindowAnimation):
    def apply(self, display):
        progression = (time.time() - self.start_time)/self.duration
        if progression > 1:
            return

        height = max(1,int(display.pixels.shape[1] * progression))

        display.pixels[:,:height] = display.pixels[:,-height:]
        display.pixels[:,height:] = self.start_pixels[:,height:]

class SlideUp(WindowAnimation):
    def apply(self, display):
        progression = (time.time() - self.start_time)/self.duration
        if progression > 1:
            return

        height = max(1,int(display.pixels.shape[1] * (1-progression)))

        display.pixels[:,:height] = self.start_pixels[:,-height:]
        display.pixels[:,height:] = display.pixels[:,height:]

class IOManager:
    def __init__(self, controller, display, fps=30, animation_duration=0.25):
        self.controller = controller
        self.display = display
        self.running = True
        self.applications = None
        self.fps = fps
        self.last_frame = display.pixels
        self.last_update = time.time()
        self.animation_duration = animation_duration
        self.current_animation = None

    def run(self, application):
        """Runs an application. Should only be invoked with the root
        application, all further applications can then be called with 
        `openApplication`.

        Args:
            application ([type]): [description]
        """
        self.applications = [application]
        last = time.time()
        delta = 0
        while len(self.applications) > 0:
            now = time.time()
            delta = now - last
            last = now
            self.update()
            self.applications[-1].update(self, delta)

            if self.current_animation is not None:
                if self.current_animation.is_finished():
                    self.current_animation = None
                else:
                    self.current_animation.apply(self.display)
            
            self.display.refresh()
            if self.controller.menu.get_fresh_value():
                self.closeApplication()
            time.sleep(max(0, min(delta, 1/self.fps)))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.running = False
        while len(self.applications) > 0:
            self.closeApplication()
        self.destroy()

    def openApplication(self, application):
        """Opens a new application

        Args:
            application (application.core.Application): The application to be opened
        """
        self.current_animation = SlideDown(self.display, self.animation_duration)
        self.applications.append(application)

    def closeApplication(self):
        """Closes the topmost application and returns to the previously opened appplication.
        If none exists quits the Program
        """
        if len(self.applications) > 0:
            self.current_animation = SlideUp(self.display, self.animation_duration)
            self.applications[-1].destroy()
            self.applications = self.applications[:-1]
        if len(self.applications) == 0:
            self.running = False

    def update(self):
        pass

    def destroy(self):
        pass
