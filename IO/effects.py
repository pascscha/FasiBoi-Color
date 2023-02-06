"""Effects that can be applied on entire display, regardles of current application
"""
import time
import numpy as np
import cv2
import math


class WindowEffect:
    """An Effect that can be applied on the entire display, regardless of the current application"""

    def __init__(self, display=None, duration=None):
        if display is not None:
            self.start_pixels = display.pixels

        self.duration = duration
        if duration is not None:
            self.start_time = time.time()

    def is_finished(self):
        """Checks whether the effect has finished"""
        if self.duration is None:
            return False
        return time.time() >= self.start_time + self.duration

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        raise NotImplementedError("Please Implement this method")


class EffectCombination:
    """A combination of multiple effects"""

    def __init__(self, effects):
        self.effects = effects

    def is_finished(self):
        """Checks whether the effects have finished"""
        return all([a.is_finished for a in self.effects])

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        for a in self.effects:
            a.apply(display)


class SlideDown(WindowEffect):
    """Slides the initial screen down and reveals the current screen"""

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        progression = (time.time() - self.start_time) / self.duration
        if progression > 1:
            return

        height = max(1, int(display.pixels.shape[1] * progression))

        display.pixels[:, :height] = display.pixels[:, -height:]
        display.pixels[:, height:] = self.start_pixels[:, height:]


class SlideUp(WindowEffect):
    """Slides the initial screen up and reveals the current screen"""

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        progression = (time.time() - self.start_time) / self.duration
        if progression > 1:
            return

        height = max(1, int(display.pixels.shape[1] * (1 - progression)))

        display.pixels[:, :height] = self.start_pixels[:, -height:]
        display.pixels[:, height:] = display.pixels[:, height:]


class Squeeze(WindowEffect):
    """Squeezes the initial screen horizontally and reveals the current screen"""

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        progression = (time.time() - self.start_time) / self.duration
        if progression > 1:
            return

        height = max(1, int(display.pixels.shape[1] * (1 - progression)))

        squeezed = cv2.resize(self.start_pixels, (height, display.pixels.shape[0]))
        top = (display.pixels.shape[1] - height) // 2

        display.pixels[:, top : top + height] = squeezed


class Minimize(WindowEffect):
    """Squeezes the initial screen horizontally and reveals the current screen"""

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        progression = (time.time() - self.start_time) / self.duration
        if progression > 1:
            return

        height = max(1, int(display.pixels.shape[1] * (1 - progression)))
        width = max(1, int(display.pixels.shape[0] * (1 - progression)))

        squeezed = cv2.resize(self.start_pixels, (height, width))

        left = (display.pixels.shape[0] - width) // 2

        display.pixels[
            left : left + width, display.pixels.shape[1] - height :
        ] = squeezed


class Noise(WindowEffect):
    """Adds noise to the screen"""

    def __init__(self, *args, level=20, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = level

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        noise = (np.random.random((10, 15)) - 0.5) * 2 * self.level
        noisy = display.pixels.astype(np.float32)
        noisy[:, :, 0] += noise
        noisy[:, :, 1] += noise
        noisy[:, :, 2] += noise
        noisy[np.where(noisy > 255)] = 255
        noisy[np.where(noisy < 0)] = 0
        display.pixels = noisy.astype(np.uint8)


class StripedNoise(WindowEffect):
    """Adds striped noise to the screen"""

    def __init__(self, *args, coarseness=0.02, limit=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.coarseness = coarseness
        self.limit = limit
        self.noise = 0

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        img = display.pixels.astype(np.float)
        for y in range(display.height):
            for x in range(display.width):
                self.noise += (np.random.random() - 0.5) * 2 / self.coarseness
                if self.noise > self.limit:
                    self.noise = 2 * self.limit - self.noise
                if self.noise < -self.limit:
                    self.noise = -2 * self.limit - self.noise
                img[x, y] += self.noise

        img[np.where(img > 255)] = 255
        img[np.where(img < 0)] = 0
        display.pixels = img.astype(np.uint8)


class VerticalDistort(WindowEffect):
    """Randomly offsets vertical rows"""

    def __init__(self, *args, amount=2, frequency=1 / 10, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount = amount
        self.frequency = frequency

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        amount = 0
        for y in range(display.height):
            rand = np.random.random()
            if rand < self.frequency:
                amount += int((np.random.random() - 0.5) * 2 * self.amount)

            if amount > 0:
                display.pixels[amount:, y] = display.pixels[:-amount, y]
                # display.pixels[:amount, y] = 0
            elif amount < 0:
                display.pixels[:amount, y] = display.pixels[-amount:, y]
                # display.pixels[-amount:, y] = 0


class Dropout(WindowEffect):
    """Randomly makes some pixels black"""

    def __init__(self, *args, frequency=1 / 2, **kwargs):
        super().__init__(*args, **kwargs)
        self.frequency = frequency

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        for y in range(display.height):
            rand = np.random.random()
            if rand < self.frequency:
                display.pixels[:, y] = 0


class Black(WindowEffect):
    """Makes entire screen black"""

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        display.pixels[:] = 0


class Notch(WindowEffect):
    """Creates an IPhone like Notch for Apple fans"""

    def apply(self, display):
        """
        Applies the effect to the current display
        Args:
            display: The current state of the display
        """
        display.pixels[3:7, 0] = 0


class ColorPalette(WindowEffect):
    def __init__(self, *args, colors=[(0, 0, 0), (255, 255, 255)], **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors

    @staticmethod
    def squared_distances(frame, color):
        d1 = frame[:, :, 0] - color[0]
        d2 = frame[:, :, 1] - color[1]
        d3 = frame[:, :, 2] - color[2]
        return np.sqrt(d1**2 + d2**2 + d3**2)

    def apply(self, display):
        scores = [
            self.squared_distances(display.pixels.astype(np.int32), color).reshape(-1)
            for color in self.colors
        ]

        sort_me = [
            (scores[c][i], i, c)
            for c in range(len(self.colors))
            for i in range(display.width * display.height)
        ]
        sort_me.sort(key=lambda x: x[0], reverse=False)

        max_count = math.ceil(display.width * display.height / len(self.colors))
        counts = [0] * len(self.colors)
        last_distances = [100000000] * len(self.colors)
        for d, i, c in sort_me:
            if counts[c] <= max_count or d == last_distances[c]:
                display.pixels[i // display.height][i % display.height] = self.colors[c]
                counts[c] += 1
                last_distances[c] = d
        """



        # min_distances = [np.min(d) for d in distances]
        # max_distances = [np.max(d) for d in distances]
        # scores = np.array([(distance - min_distance) / (max_distance - min_distance) for distance, min_distance, max_distance in zip(distances, min_distances, max_distances)])
        indices = np.argmin(scores, axis=0)
        for i, c in enumerate(self.colors):
            display.pixels[np.where(indices==i)] = c
        """
