"""Core IO Management
"""
import time
import numpy as np
from IO.effects import (
    EffectCombination,
    VerticalDistort,
    StripedNoise,
    Dropout,
    Black,
    SlideUp,
    SlideDown,
    ColorPalette,
    Notch,
    Squeeze,
    Minimize,
)
from IO.color import Color
import cv2
import json
import os


class ControllerValue:
    """The value of a controller"""

    def __init__(self, dtype=bool, default=False):
        self._value = default
        self.fresh = False
        self.last_change = time.time()
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
            self.last_change = time.time()

    def get_value(self):
        """Gets the current value of the button/input

        Returns:
            self.dtype: The current Value of the controller
        """
        self.fresh = False
        return self._value

    def get_fresh_value(self):
        """Gets the current value of that button/input, if it has not been accessed yet (if it's
        fresh).
        Otherwise returns None

        Returns:
            self.dtype: The value of the button/input if it has not been accessed yet, otherwise
            None
        """
        if self.fresh:
            self.fresh = False
            return self._value
        return None


class BooleanControllerValue(ControllerValue):
    """A Controller value that only has a boolean state, e.g. a Button"""

    TIMEOUT = 2

    def update_true(self):
        # print("Set to true")
        self.update(1)

    def update_false(self):
        # print("Set to false")
        self.update(0)

    def fresh_press(self):
        """Checks if the button has freshly been pressed"""
        if self._value and self.fresh and self.last_change + self.TIMEOUT > time.time():
            self.fresh = False
            return True
        return False

    def fresh_release(self):
        """Checks if the button has freshly been released"""
        if (
            not self._value
            and self.fresh
            and self.last_change + self.TIMEOUT > time.time()
        ):
            self.fresh = False
            return True
        return False


class Controller:
    """The Base class for a controller, holding several controller values"""

    def __init__(self):
        self.button_up = BooleanControllerValue()
        self.button_right = BooleanControllerValue()
        self.button_down = BooleanControllerValue()
        self.button_left = BooleanControllerValue()
        self.button_a = BooleanControllerValue()
        self.button_b = BooleanControllerValue()
        self.button_menu = BooleanControllerValue()
        self.button_teppich = BooleanControllerValue()


class Display:
    """The Base class for a display, showing the current state of the application"""

    def __init__(self, width, height, brightness=1):
        self.width = width
        self.height = height
        self.pixels = np.zeros((width, height, 3), dtype=np.uint8)
        self.last_pixels = np.ones((width, height, 3), dtype=np.uint8)
        self.brightness = brightness

    def force_update(self):
        """Forces all pixels to be redrawn, even if they might have not changed"""
        self.last_pixels = np.ones((self.width, self.height, 3), dtype=np.uint8)

    def check_coordinates(self, x, y):
        """Checks wether the given coordinates are valid

        Args:
            x (int): X coordinate
            y (int): Y coordinate

        Raises:
            ValueError: If X or Y coordinates are out of bounds
        """
        if x < 0 or x >= self.width:
            raise ValueError("x Coordinates out of bounds!")
        if y < 0 or y >= self.height:
            raise ValueError("y Coordinates out of bounds!")

    @staticmethod
    def check_color(color):
        """Checks wether a color is valid

        Args:
            color ((int, int, int)): The color

        Raises:
            ValueError: If the color is not properly formatted
        """
        if min(color) < 0 or max(color) >= 256:
            raise ValueError("Colors have to be between 0 and 255")
        if len(color) != 3:
            raise ValueError("Colors must have 3 channels")

    def update(self, x, y, color):
        """Updates single pixel on the screen

        Args:
            x (int): The x coordinate of that pixel
            y (int): The y coordinate of that pixel
            color ((int, int, int)): The new rgb color of that pixel
        """
        self.check_coordinates(x, y)
        if not isinstance(color, Color):
            color = Color(*color)
        self.pixels[x][y] = color

    def fill(self, color):
        """Fills the entire screen with one color

        Args:
            color ((int, int, int)): The rgb color to fill the screen with
        """
        if not isinstance(color, Color):
            color = Color(*color)
        color = tuple(color)

        self.pixels = np.ones((self.width, self.height, 3), dtype=np.uint8) * color

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
            self._update(x, y, self.pixels[x][y] * self.brightness)
        self.last_pixels = self.pixels.copy()
        self._refresh()


class IOManager:
    """The IOManager, that controls the applications and provides them with access to controler and
    display
    """

    def __init__(
        self,
        controller,
        display,
        fps=20,
        animation_duration=0.25,
        record_path=None,
        record_scale=10,
        expected_battery_life=60,
    ):
        self.running_uncharged = self.load_running_uncharged()
        self.expected_battery_life = expected_battery_life
        self.controller = controller
        self.display = display
        self.running = True
        self.applications = None
        self.fps = fps
        self.last_frame = display.pixels
        self.last_update = time.time()
        self.animation_duration = animation_duration
        self.current_animation = None
        self.color_palette = None

        self.teppich = 0
        self.teppich_animations = [
            None,
            Notch(),
            EffectCombination(
                [VerticalDistort(frequency=1 / 60), StripedNoise(limit=50)]
            ),
            EffectCombination([VerticalDistort(), StripedNoise(limit=100)]),
            EffectCombination(
                [
                    VerticalDistort(amount=4),
                    StripedNoise(limit=200),
                    Dropout(frequency=1 / 2),
                ]
            ),
            Black(),
        ]

        # Start recording if necessary
        self.video_out = None
        if record_path is not None:
            self.record_shape = (
                display.width * record_scale,
                display.height * record_scale,
            )
            if record_path.lower().endswith(".avi"):
                self.video_out = cv2.VideoWriter(
                    record_path, cv2.VideoWriter_fourcc(*"MJPG"), fps, self.record_shape
                )
            elif record_path.lower().endswith(".mp4"):
                self.video_out = cv2.VideoWriter(
                    record_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, self.record_shape
                )

    @staticmethod
    def load_running_uncharged():
        if os.path.exists("resources/appdata/Core.json"):
            with open("resources/appdata/Core.json") as f:
                return json.load(f).get("running_uncharged", 0)
        return 0

    def set_battery(self, battery):
        self.running_uncharged = (1 - battery) * self.expected_battery_life

    def set_fully_charged(self):
        self.running_uncharged = 0

    def run(self, application):
        """Runs an application. Should only be invoked with the root
        application, all further applications can then be called with
        `openApplication`.

        Args:
            application ([type]): [description]
        """
        self.applications = [application]
        last = time.time()
        mfps = self.fps
        while len(self.applications) > 0:
            now = time.time()
            delta = now - last
            last = now
            self.update()

            if not self.applications[-1].is_sleeping(delta):
                self.applications[-1].update(self, delta)

                if self.applications[-1].MAX_FPS is not None:
                    fps = min(self.fps, self.applications[-1].MAX_FPS)
                else:
                    fps = self.fps

            # Apply Effects
            if self.current_animation is not None:
                if self.current_animation.is_finished():
                    self.current_animation = None
                else:
                    self.current_animation.apply(self.display)
                    fps = self.fps

                    # Wake application up
                    self.applications[-1].wakers = None

            # Apply Drunkguard
            if self.controller.button_teppich.fresh_press():
                self.teppich = (self.teppich + 1) % len(self.teppich_animations)

            if self.teppich_animations[self.teppich] is not None:
                self.teppich_animations[self.teppich].apply(self.display)
                fps = self.fps

            # Apply Color Palette
            if self.color_palette is not None:
                self.color_palette.apply(self.display)

            # Update display
            self.display.refresh()

            # Close application if button is pressed
            if self.controller.button_menu.fresh_press():
                self.close_application()

            # Save frame to recording
            if self.video_out is not None:
                out = cv2.resize(
                    self.display.pixels.transpose(1, 0, 2),
                    self.record_shape,
                    interpolation=cv2.INTER_NEAREST,
                )
                self.video_out.write(cv2.cvtColor(out, cv2.COLOR_RGB2BGR))

            # Sleep for the rest of the frame
            calc_duration = time.time() - last
            # mfps = (10 * mfps + 1 / calc_duration) / 11
            # print("max FPS", int(mfps), "\tFPS", int(fps))

            time.sleep(max(0, 1 / fps - calc_duration))

            self.running_uncharged += calc_duration + max(0, 1 / fps - calc_duration)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):

        with open("resources/appdata/Core.json", "w+") as f:
            json.dump({"running_uncharged": self.running_uncharged}, f)

        self.running = False
        while len(self.applications) > 0:
            self.close_application()

        if self.video_out is not None:
            self.video_out.release()

        self.destroy()

    def open_application(self, application):
        """Opens a new application

        Args:
            application (application.core.Application): The application to be opened
        """
        self.current_animation = SlideDown(self.display, self.animation_duration)
        self.applications.append(application)

    def close_application(self):
        """Closes the topmost application and returns to the previously opened appplication.
        If none exists quits the Program
        """
        if len(self.applications) > 1:
            self.current_animation = Minimize(self.display, self.animation_duration)
            self.applications = self.applications[:-1]
        if len(self.applications) == 0:
            self.running = False

    def update(self):
        """Update function that gets called every frame"""

    def destroy(self):
        """Cleanup function that gets called after all applications are closed"""

    def get_battery(self):
        """Calculates the current battery, returns value between 0 (empty) and 1 (fully charged)"""
        return min(1, max(0, 1 - self.running_uncharged / self.expected_battery_life))
