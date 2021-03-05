import time
from numpy import load
from applications import _BaseApplication, controllerInput

class BeatFeeler:
    def __init__(self, controllerValue):
        controllerValue.subscribe(self.beat)
        self.last = time.time()
        self.duration = 1
        self.beat_count = 0

    def beat(self, on):
        if on:
            now = time.time()
            self.beat_count += round((now - self.last) / self.duration)
            self.duration = now - self.last
            self.last = now

    def getProgression(self):
        now = time.time()
        return self.beat_count + (now - self.last) / self.duration


class BeatAnimation(_BaseApplication):
    def __init__(self, npy_path, ioManager, beats_per_loop=1):
        self.beatFeeler = BeatFeeler(ioManager.controller.b)
        self.disp = ioManager.display
        self.animation = load(npy_path)
        self.animation_length = len(self.animation)
        self.beat_frames = self.animation_length / beats_per_loop

    def update(self):
        frame = self.animation[int(self.beatFeeler.getProgression(
        )*self.beat_frames) % self.animation_length]

        for x in range(frame.shape[0]):
            for y in range(frame.shape[1]):
                if frame[x][y]:
                    self.disp.update(y,x, (255,255,255))
                else:
                    self.disp.update(y,x, (0,0,0))

class AnimationCycler:
    def __init__(self, ioManager, animations):
        self.animations = animations
        ioManager.controller.a.subscribe(self.cycle)
        self.index = 0
    
    @controllerInput
    def cycle(self, value):
        if value:
            self.index = (self.index + 1) % len(self.animations)
    
    def update(self):
        self.animations[self.index].update()