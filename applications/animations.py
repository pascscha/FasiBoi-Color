import time
from numpy import load
from applications import core
import colorsys

class BeatFeeler:
    def __init__(self, controllerValue):
        controllerValue.subscribe(self.beat)
        self.last = time.time()
        self.duration = 0.5
        self.beat_count = 0

    def beat(self, _, on):
        if on:
            now = time.time()
            self.beat_count += round((now - self.last) / self.duration)
            self.duration = now - self.last
            self.last = now

    def getProgression(self):
        now = time.time()
        return self.beat_count + (now - self.last) / self.duration


class BeatAnimation(core.Application):
    def __init__(self, npy_path, ioManager, beats_per_loop=1):
        self.beatFeeler = BeatFeeler(ioManager.controller.b)
        self.disp = ioManager.display
        self.animation = load(npy_path)
        self.animation_length = len(self.animation)
        self.beat_frames = self.animation_length / beats_per_loop
        self.hue = 0
        self.last = time.time()
    
    def update(self):
        frame = self.animation[int(self.beatFeeler.getProgression(
        )*self.beat_frames) % self.animation_length]

        now = time.time()
        diff = now - self.last
        self.last = now

        self.hue += diff/2
        self.hue = self.hue %255
        color = tuple(map(lambda x:int(x*255),colorsys.hsv_to_rgb(self.hue, 1, 0.125)))
        
        for x in range(frame.shape[0]):
            for y in range(frame.shape[1]):
                if frame[x][y]:
                    self.disp.update(y,x, color)
                else:
                    self.disp.update(y,x, (0,0,0))
        self.disp.refresh()

class AnimationCycler(core.Application):
    def __init__(self, animations, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animations = animations
        self.io.controller.a.subscribe(self.cycle)
        self.index = 0
    
    @core.controllerInput
    def cycle(self, value):
        if value:
            self.index = (self.index + 1) % len(self.animations)
    
    def update(self):
        self.animations[self.index].update()

class SolidColor(core.Application):
    def __init__(self, color, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.color = color
        self.brightness = 0
        self.last = time.time()
        self.up = True 

    def update(self):
        now = time.time()
        diff = now - self.last
        if not self.up:
            diff *= -1
        self.brightness += diff*300
        if self.brightness > 255:
            self.brightness = 255
            self.up = not self.up
        elif self.brightness < 0:
            self.brightness = 0
            self.up = not self.up
        self.last = now


        for x in range(self.io.display.width):
            for y in range(self.io.display.height):
                self.io.display.update(x, y, (255, 255, 255))
        self.io.display.refresh()
        """self.io.display.update(4, 14, (int(self.brightness), 0, 0))
        self.io.display.update(5, 14, (0, int(self.brightness), 0))
        self.io.display.update(6, 14, (0, 0, int(self.brightness)))
        self.io.display.update(7, 14, (0, int(self.brightness), int(self.brightness)))
        self.io.display.update(8, 14, (int(self.brightness), 0, int(self.brightness)))
        self.io.display.update(9, 14, (int(self.brightness), int(self.brightness), 0))
        self.io.display.update(6, 14, (0, 0, 0))
        self.io.display.refresh()
        """