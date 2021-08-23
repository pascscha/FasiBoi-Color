import time
import numpy as np
import cv2


class WindowEffect:
    def __init__(self, display=None, duration=None):
        if display is not None:
            self.start_pixels = display.pixels

        self.duration = duration
        if duration is not None:
            self.start_time = time.time()

    def is_finished(self):
        if self.duration is None:
            return False
        else:
            return time.time() >= self.start_time + self.duration

    def apply(self, display):
        raise NotImplementedError("Please Implement this method")


class EffectCombination:
    def __init__(self, effects):
        self.effects = effects

    def is_finished(self):
        return all([a.is_finished for a in self.effects])

    def apply(self, display):
        for a in self.effects:
            a.apply(display)


class SlideDown(WindowEffect):
    def apply(self, display):
        progression = (time.time() - self.start_time) / self.duration
        if progression > 1:
            return

        height = max(1, int(display.pixels.shape[1] * progression))

        display.pixels[:, :height] = display.pixels[:, -height:]
        display.pixels[:, height:] = self.start_pixels[:, height:]


class SlideUp(WindowEffect):
    def apply(self, display):
        progression = (time.time() - self.start_time) / self.duration
        if progression > 1:
            return

        height = max(1, int(display.pixels.shape[1] * (1 - progression)))

        display.pixels[:, :height] = self.start_pixels[:, -height:]
        display.pixels[:, height:] = display.pixels[:, height:]


class Squeeze(WindowEffect):
    def apply(self, display):
        progression = (time.time() - self.start_time) / self.duration
        if progression > 1:
            return

        height = max(1, int(display.pixels.shape[1] * (1 - progression)))

        squeezed = cv2.resize(
            self.start_pixels, (height, display.pixels.shape[0]))
        top = (display.pixels.shape[1] - height) // 2

        display.pixels[:, top:top + height] = squeezed


class Noise(WindowEffect):
    def __init__(self, *args, level=20, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = level

    def apply(self, display):
        noise = (np.random.random((10, 15)) - 0.5) * 2 * self.level
        noisy = display.pixels.astype(np.float32)
        noisy[:, :, 0] += noise
        noisy[:, :, 1] += noise
        noisy[:, :, 2] += noise
        noisy[np.where(noisy > 255)] = 255
        noisy[np.where(noisy < 0)] = 0
        display.pixels = noisy.astype(np.uint8)


class StripedNoise(WindowEffect):
    def __init__(self, *args, coarseness=0.02, limit=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.coarseness = coarseness
        self.limit = limit
        self.noise = 0

    def apply(self, display):
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
    def __init__(self, *args, amount=2, frequency=1 / 10, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount = amount
        self.frequency = frequency

    def apply(self, display):
        amount = 0
        for y in range(display.height):
            rand = np.random.random()
            if rand < self.frequency:
                amount += int((np.random.random() - 0.5) * 2 * self.amount)

            if amount > 0:
                display.pixels[amount:, y] = display.pixels[:-amount, y]
                #display.pixels[:amount, y] = 0
            elif amount < 0:
                display.pixels[:amount, y] = display.pixels[-amount:, y]
                #display.pixels[-amount:, y] = 0


class Dropout(WindowEffect):
    def __init__(self, *args, frequency=1 / 2, **kwargs):
        super().__init__(*args, **kwargs)
        self.frequency = frequency

    def apply(self, display):
        for y in range(display.height):
            rand = np.random.random()
            if rand < self.frequency:
                display.pixels[:, y] = 0


class Black(WindowEffect):
    def apply(self, display):
        display.pixels[:] = 0
