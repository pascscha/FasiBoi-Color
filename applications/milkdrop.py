from applications import core
from helpers import animations, bitmaputils
from IO.color import *
import time
import numpy
import cv2
import random

class Provider:
    ENERGY = 0.5
    def __init__(self, shape):
        self.shape = shape
    
    def get_frame(self, delta, progression, beat):
        raise NotImplementedError("Please Implement this Method")

class Blinker(Provider):
    def __init__(self, *args, coords=[(5, 7)], **kwargs):
        super().__init__(*args, **kwargs)
        self.black = np.zeros(self.shape) 
        self.coords = coords

    def _get_frame(self, color):
        out = self.black.copy()
        for c in self.coords:
            out[c] = color
        return out

    def get_frame(self, delta, progression, beat):
        if beat == True:
            return self._get_frame(WHITE)
        else:
            return self._get_frame(Color(1,1,1))

class Blinker2(Blinker):
    def __init__(self, *args, color=WHITE, fun=lambda x:(1-x)**2, **kwargs):
        super().__init__(*args, **kwargs)
        self.fun = fun
        self.color = color

    def get_frame(self, delta, progression, beat):
        return self._get_frame(self.color*self.fun(progression))

class ColorBlinker(Blinker2):
    def __init__(self, *args, color_cycle=8, **kwargs):
        super().__init__(*args, **kwargs)
        self.beat_count = 0
        self.color_cycle = color_cycle

    def get_frame(self, delta, progression, beat):
        if beat:
            self.beat_count = (self.beat_count + 1) % self.color_cycle
        hue = (self.beat_count + progression) / self.color_cycle
        color = Color.from_hsv(hue, 1, self.fun(progression))
        return self._get_frame(color)

class RandomBlinker(Provider):
    def __init__(self, blinker, *args, n_active=10, change_interval=4, **kwargs):
        super().__init__(blinker.shape, *args, **kwargs)
        self.blinker = blinker
        self.change_interval = change_interval
        self.n_active = n_active
        self.all_coords = [(x,y) for x in range(self.shape[0]) for y in range(self.shape[1])]
        self.blinker.coords = random.sample(self.all_coords, self.n_active)
        self.beat_count = 0

    def get_frame(self, delta, progression, beat):
        if beat:
            self.beat_count += 1
        if self.beat_count >= self.change_interval:
            self.beat_count -= self.change_interval
            self.blinker.coords = random.sample(self.all_coords, self.n_active)
        return self.blinker.get_frame(delta, progression, beat)

class Particles(Provider):
    def __init__(self, *args, path=[(5, 7)], n_particles = 2, fun=lambda x:(1-x)**2, speed=1, radius=2, color_cycle=8, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.fun=fun
        self.n_particles = n_particles
        self.ticker = animations.Ticker(speed)
        self.black = np.zeros(self.shape) 
        self.radius = radius
        self.color_cycle = color_cycle
        self.beat_count = 0
    
    def get_frame(self, delta, progression, beat):
        self.ticker.tick(delta * (1 - progression))

        if beat:
            self.beat_count = (self.beat_count + 1) % self.color_cycle


        out = self.black.copy()
        #for coord in self.path:
        #    out[coord] = Color(1,1,1)

        for i in range(self.n_particles):
            prog = self.ticker.progression + i/self.n_particles
            prog -= int(prog)
            index = int(prog * len(self.path))
            hue = (self.beat_count + progression) / self.color_cycle
            hue = hue - int(hue)
            x, y = self.path[index]
            for px in range(x, x+self.radius):
                for py in range(y, y+self.radius):
                    px = max(0, min(self.shape[0]-1, px))
                    py = max(0, min(self.shape[1]-1, py))
                    out[px, py] = Color.from_hsv(hue, 1, self.fun(progression))
        return out

class Distorter:
    ENERGY = 0.5

    def __init__(self, shape, speed=10):
        self.shape = shape
        self.ticker = animations.Ticker(speed)

def down(w, h, x, y):
    return (0, -1)

def up(w, h, x, y):
    return (0, 1)

def to_center(w, h, x, y):
    return -(w/2-x), -(h/2-y)

def from_center(w, h, x, y):
    return (w/2-x), (h/2-y)

def swirl(w, h, x, y):
    return h/2 - y, x - w/2

class Wave(Distorter):
    def __init__(self, *args, speed=6, pred=to_center, **kwargs):
        super().__init__(*args, **kwargs)
        self.cx = self.shape[0]//2
        self.cy = self.shape[1]//2
        self.speed = speed
        
        self.pred_map = {}
        for x in range(self.shape[0]):
            for y in range(self.shape[1]):
                self.pred_map[(x, y)] = pred(self.shape[0], self.shape[1], x, y)

    def distort(self, delta, last_frame, frame, progression, beat):
        cx = self.shape[0]//2
        cy = self.shape[1]//2


        out = last_frame.copy()

        for x in range(self.shape[0]):
            for y in range(self.shape[1]):            
                vx, vy = self.pred_map[(x, y)]
                px = x + vx * self.speed * delta
                py = y + vy * self.speed * delta
                c = bitmaputils.getAntialiasedColor(last_frame, (px, py))
                out[x, y] = bitmaputils.getAntialiasedColor(last_frame, (px, py))

        nonzero_coords = np.where(np.any(frame != [0, 0, 0], axis=2))
        out[nonzero_coords] = frame[nonzero_coords]   

        return out

class Visualization:
    def __init__(self, provider, distorter, energy=0.5):
        self.provider = provider
        self.distorter = distorter
        self.energy = energy

class Milkdrop(core.Application):
    ENERGY_GRANULARITY = 10
    BEAT_MEMORY_SIZE = 4
    SIZE = (10, 15)
    
    def __init__(self):
        self.beat_duration = 0.5
        self.energy = 0.5
        now = time.time()
        self.beat = False
        self.last_click = now
        self.last_beats = [now - i*self.beat_duration for i in range(self.BEAT_MEMORY_SIZE)]
        
        center = [(self.SIZE[0]//2, self.SIZE[1]//2)]

        edge = [(x, 0) for x in range(self.SIZE[0])] + \
                 [(self.SIZE[0]-1, y) for y in range(1, self.SIZE[1])] + \
                 [(x, self.SIZE[1]-1) for x in range(self.SIZE[0]-2, 0,-1)] + \
                 [(0, y) for y in range(self.SIZE[1]-1,0,-1)]

        all_coords = [(x, y) for x in range(self.SIZE[0]) for y in range(self.SIZE[1])]
        shape = (*self.SIZE, 3)
        self.last_frame = np.zeros(shape)

        # Visualizations
        self.visualizations = [
            Visualization(
                ColorBlinker(shape, coords = edge),
                Wave(shape, pred=to_center)),
            Visualization(
                RandomBlinker(ColorBlinker(shape, coords = edge), change_interval=1),
                Wave(shape, pred=swirl)),
            Visualization(
                Particles(shape, path=edge, n_particles=4),
                Wave(shape, pred=to_center, speed=2)),
            Visualization(
                RandomBlinker(Blinker(shape), n_active=50),
                Wave(shape, pred=from_center)),
            Visualization(
                Particles(shape, path=all_coords, n_particles=16, speed=0.1, radius=1),
                Wave(shape, pred=up, speed=2)),
            Visualization(
                Particles(shape, path=all_coords, n_particles=16, speed=0.2, radius=1),
                Wave(shape, pred=from_center, speed=2)),
            Visualization(
                RandomBlinker(Blinker2(shape, color=BLUE), n_active=10, change_interval=1),
                Wave(shape, pred=down)),
            Visualization(
                ColorBlinker(shape, coords = center),
                Wave(shape, pred=from_center)),
            Visualization(
                Blinker2(shape, coords = center, fun=lambda x:(1-x)**4),
                Wave(shape, pred=from_center)),

        ]
        self.visualization_index = len(self.visualizations) - 1

    def update(self, io, delta):
        if io.controller.up.get_fresh_value() == False:
            self.energy = min(1, self.energy + 1/self.ENERGY_GRANULARITY)

        if io.controller.down.get_fresh_value() == False:
            self.energy = max(0, self.energy - 1/self.ENERGY_GRANULARITY)

        if io.controller.right.get_fresh_value() == True:
            self.visualization_index = (self.visualization_index + 1) % len(self.visualizations)

        if io.controller.left.get_fresh_value() == True:    
            self.visualization_index = (self.visualization_index - 1) % len(self.visualizations)


        if io.controller.b.get_fresh_value() == True:
            self.visualization_index = random.randint(0, len(self.visualizations)-1)

        now = time.time()

        if io.controller.a.get_fresh_value() == True:
            
            click_duration = now - self.last_click
            # Check if last click was recently
            if click_duration < 10:
                # If Clicking and beat roughly at the same speed, just correct
                if 0.75 < click_duration / self.beat_duration < 1.33:
                    
                    diff1 = abs(now - (self.last_beats[0] + self.beat_duration))
                    diff2 = abs(now - self.last_beats[0])
                    if diff1 > diff2:
                        # Slightly slower that the current beat, correct current beat
                        self.last_beats[0] = now
                    else:
                        # Slightly faster that the current beat, add new beat now
                        self.beat = True
                        self.last_beats = [now] + self.last_beats[:self.BEAT_MEMORY_SIZE - 1]
                else:
                    # Clicking and beat drastically different speeds, change tempo
                    self.beat_duration = click_duration
                    self.beat = True
                    self.last_beats = [now - i*self.beat_duration for i in range(self.BEAT_MEMORY_SIZE)]
            self.last_click = now
        else:
            now = time.time()
            if self.last_beats[0] + self.beat_duration < now:
                self.beat = True
                self.last_beats = [self.last_beats[0] + self.beat_duration] + self.last_beats[:self.BEAT_MEMORY_SIZE - 1]
            else:
                self.beat = False

        progression = (now - self.last_beats[0]) / self.beat_duration
        viz = self.visualizations[self.visualization_index]
        animation = viz.provider.get_frame(delta, progression, self.beat)
        distorted = viz.distorter.distort(delta, self.last_frame, animation, progression, self.beat)
        self.last_frame = distorted
        io.display.pixels = distorted
