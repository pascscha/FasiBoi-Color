from applications import core
from helpers import animations, bitmaputils
from IO.color import *
import time
import numpy
import cv2
import random
import math

class MilkdropValue():
    def get_value(self, delta, progression, beat):
        raise NotImplementedError("Please Implement this method!")

class ConstantValue(MilkdropValue):
    def __init__(self, value):
        self.value = value
    
    def get_value(self, delta, progression, beat):
        return self.value

class AnimatedValue(MilkdropValue):
    def __init__(self, *args, fun1=lambda x:x**2, fun2=lambda x:1-x, period=1, offset=0,**kwargs):
        self.beat_count = 0
        self.fun1 = fun1
        self.fun2 = fun2
        self.period = period
        self.offset = offset
    
    def get_value(self, delta, progression, beat):
        if beat:
            self.beat_count = (self.beat_count + 1) % self.period
        return self.fun2((self.beat_count + self.fun1(progression)) / self.period)

class AnimatedHSVColor():
    def __init__(self, *args, h=AnimatedValue(period=8), s=ConstantValue(1), v=AnimatedValue(), **kwargs):
        super().__init__(*args, **kwargs)
        self.h = h
        self.s = s
        self.v = v

    def get_value(self, delta, progression, beat):
        return Color.from_hsv(
            self.h.get_value(delta, progression, beat),
            self.s.get_value(delta, progression, beat),
            self.v.get_value(delta, progression, beat)
        )

class Content:
    def apply(self, frame, delta, progression, beat):
        raise NotImplementedError()

class Drawer(Content):
    def __init__(self, color=AnimatedHSVColor(), coords=[(5,7)], radius=1):
        self.color = color
        self.coords = coords
        self.radius = radius
        self.radius1 = math.floor(radius/2)
        self.radius2 = math.ceil(radius/2)
    
    def apply(self, frame, delta, progression, beat):
        color = self.color.get_value(delta, progression, beat)
        for x, y in self.coords:
            frame[max(0, x-self.radius1):min(frame.shape[0], x+self.radius2),
                  max(0, y-self.radius1):min(frame.shape[1], y+self.radius2)] = color
        return frame

class RandomDrawer(Drawer):
    def __init__(self, *args, period=4, particles=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = period
        self.particles = particles
        self.beat_count = 0

    def apply(self, frame, delta, progression, beat):
        if beat:
            self.beat_count += 1
            if self.beat_count % self.period == 0:
                self.coords = [(random.randint(0,frame.shape[0]-1), random.randint(0,frame.shape[1]-1)) for _ in range(self.particles)]
        return super().apply(frame, delta, progression, beat)

class Particles(Drawer):
    def __init__(self, *args, path=[(5, 7)], particles=10, position=AnimatedValue(period=4), **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.particles = particles
        self.position = position
    
    def apply(self, frame, delta, progression, beat):
        pos = self.position.get_value(delta, progression, beat)
        color = self.color.get_value(delta, progression, beat)
        self.coords = [self.path[int((pos + i/self.particles) * len(self.path)) % len(self.path)] for i in range(self.particles)]
        return super().apply(frame, delta, progression, beat)

class Animation(Drawer):
    def __init__(self, *args, driver=AnimatedValue(fun1=lambda x:x), npy_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        animation = np.load(npy_path)
        self.frame_coords = [list(zip(*reversed(np.where(frame)))) for frame in animation]
        self.animation_length = len(animation)
        self.driver = driver
    
    def apply(self, frame, delta, progression, beat):
        idx = int(self.driver.get_value(delta, progression, beat) * self.animation_length)
        self.coords = self.frame_coords[idx%self.animation_length]
        return super().apply(frame, delta, progression, beat)

class GameOfLife(Drawer):
    def __init__(self, *args, period=128, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = None
        self.period = period
        self.beat_count = 0

    @staticmethod
    def get(field, x, y):
        return field[x%field.shape[0], y%field.shape[1]]

    def apply(self, frame, delta, progression, beat):
        if beat:
            self.beat_count = (self.beat_count + 1) % self.period
            if self.beat_count == 0:
                self.field = None
        
        if self.field is None or np.all(self.field == False):
            self.field = np.zeros(frame.shape[:2], dtype=np.bool)
            for i in range(frame.shape[0]*frame.shape[1]//2):
                x = random.randint(0, frame.shape[0]-1)
                y = random.randint(0, frame.shape[1]-1)
                self.field[x][y] = True

        if beat:
            next_field = np.zeros(self.field.shape)
            for x in range(next_field.shape[0]):
                for y in range(next_field.shape[1]):
                    count = 0 + self.get(self.field, x-1, y-1) + \
                            self.get(self.field, x-1, y) + \
                            self.get(self.field, x-1, y+1) + \
                            self.get(self.field, x, y-1) + \
                            self.get(self.field, x, y+1) + \
                            self.get(self.field, x+1, y-1) + \
                            self.get(self.field, x+1, y) + \
                            self.get(self.field, x+1, y+1)
                    if count == 3:
                        next_field[x][y] = True
                    elif count == 2:
                        next_field[x][y] = self.field[x][y]
                    else:
                        next_field[x][y] = False
            self.coords = list(zip(*np.where(next_field)))

            if np.all(self.field == next_field):
                self.field = None
            else:
                self.field = next_field
        return super().apply(frame, delta, progression, beat)                    


def down(w, h, x, y):
    return (0, -1)

def up(w, h, x, y):
    return (0, 1)

def up_wave(w, h, x, y):
    return (y%3-1, 1)
    
def to_center(w, h, x, y):
    return -(w/2-x), -(h/2-y)

def from_center(w, h, x, y):
    return (w/2-x), (h/2-y)

def swirl(w, h, x, y):
    return h/2 - y, x - w/2

class Distorter(Content):
    def __init__(self, shape=(10,15), speed=6, vect_fun=to_center, darken=0):
        self.speed = speed
        self.vectors = [[vect_fun(*shape, x, y) for y in range(shape[1])] for x in range(shape[0])]
        self.darken = darken
    
    def apply(self, frame, delta, progression, beat):
        darkened = frame * (1 - self.darken)
        out = darkened.copy()

        for x in range(out.shape[0]):
            for y in range(out.shape[1]):      
                vx, vy = self.vectors[x][y]
                px = x + vx * self.speed * delta
                py = y + vy * self.speed * delta
                out[x, y] = bitmaputils.getAntialiasedColor(darkened, (px, py))
        
        return out
    

class Visualization:
    REPEAT_TIME=30
    def __init__(self, effects=[], name=None,  min_bpm=None, max_bpm=None, energy=0.5):
        self.name = name
        self.effects = effects
        self.min_bpm = min_bpm
        self.max_bpm = max_bpm
        self.energy = energy
        self.last_applied = time.time()-self.REPEAT_TIME
    
    def apply(self, frame, delta, progression, beat):
        self.last_applied = time.time()
        for effect in self.effects:
            frame = effect.apply(frame, delta, progression, beat)
        return frame

    @staticmethod
    def gaussian(x, height=1, center=0, deviation=1):
        return height * math.exp(-(x-center)**2 / (2*deviation**2))

    def is_fitting(self, bpm, energy):
        if self.min_bpm is not None and bpm < self.min_bpm:
            return 0
        elif self.max_bpm is not None and bpm > self.max_bpm:
            return 0

        now = time.time()
        energy_fit = self.gaussian(self.energy, center=energy, deviation=0.3)
        time_fit = 1-self.gaussian(now, center=self.last_applied, deviation=self.REPEAT_TIME)
        print(f"{str(self.name):>20} {energy_fit * time_fit:.2f} (e: {energy_fit:.2f}, t: {time_fit:.2f})")
        return energy_fit * time_fit

class FrameHolder:
    def __init__(self):
        self.frame = None

class PortalIn(Content):
    def __init__(self, frameHolder):
        self.frameHolder = frameHolder

    def apply(self, frame, delta, progression, beat):
        self.frameHolder.frame = frame.copy()
        return frame

class PortalOut(Content):
    def __init__(self, frameHolder):
        self.frameHolder = frameHolder

    def apply(self, frame, delta, progression, beat):
        if self.frameHolder.frame is not None:
            return self.frameHolder.frame
        else:
            return frame

class Milkdrop(core.Application):
    ENERGY_GRANULARITY = 10
    BEAT_MEMORY_SIZE = 4
    SIZE = (10, 15)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beat_duration = 0.5
        self.energy = 0.5
        now = time.time()
        self.beat_count = 0
        self.last_change = 0
        self.beat = False
        self.last_click = now
        self.last_beats = [now - i*self.beat_duration for i in range(self.BEAT_MEMORY_SIZE)]
        
        center = [(self.SIZE[0]//2, self.SIZE[1]//2)]

        edge = [(x, 0) for x in range(self.SIZE[0])] + \
                 [(self.SIZE[0]-1, y) for y in range(1, self.SIZE[1])] + \
                 [(x, self.SIZE[1]-1) for x in range(self.SIZE[0]-2, 0,-1)] + \
                 [(0, y) for y in range(self.SIZE[1]-1,0,-1)]

        circle_big = [(3, 3), (4, 3), (5, 3), (6, 3), (7, 4), (8, 5), (9, 6), (9, 7), (9, 8), (9, 9), (8, 10), (7, 11), (6, 12), (5, 12), (4, 12), (3, 12), (2, 11), (1, 10), (0, 9), (0, 8), (0, 7), (0, 6), (1, 5), (2, 4)]
        circle_medium = [(4, 5), (5, 5), (6, 6), (7, 7), (7, 8), (6, 9), (5, 10), (4, 10), (3, 9), (2, 8), (2, 7), (3, 6)]
        circle_small = [(4, 6), (5, 6), (6, 7), (6, 8), (5, 9), (4, 9), (3, 8), (3, 7)]

        all_coords = [(x, y) for x in range(self.SIZE[0]) for y in range(self.SIZE[1])]
        shape = (*self.SIZE, 3)
        self.last_frame = np.zeros(shape)

        frameHolder = FrameHolder()
        portalIn = PortalIn(frameHolder)
        portalOut = PortalOut(frameHolder)

        # Visualizations
        self.visualizations = [
            Visualization(name="Tunnel",
                energy=0.8,
                effects = [
                    Distorter(),
                    Drawer(coords=edge, color=AnimatedHSVColor()),
                ]),
            Visualization(name="Galaxy", max_bpm=200,
                energy=0.2,
                effects = [
                    Distorter(vect_fun=swirl),
                    RandomDrawer(period=1),
                ]),
            Visualization(name="Stage Lights",
            energy=0.6,
            effects = [
                Distorter(vect_fun=to_center),
                Particles(path=edge, particles=5, radius=3, position=AnimatedValue(period=8)),
            ]),
            Visualization(name="Thunderstorm",
                energy=1,
                effects = [
                    Distorter(vect_fun=from_center),
                    RandomDrawer(period=1, particles=50, color=AnimatedHSVColor(h=ConstantValue(0), s=ConstantValue(0), v=AnimatedValue(fun1=lambda x:0 if x < 0.1 else 1))),
                ]),
            Visualization(name="Woven Colors",
                energy=0.2,
                effects = [
                    Distorter(vect_fun=up),
                    Particles(path=all_coords, particles=16, position=AnimatedValue(period=50)),
                ]),
            Visualization(name="Rain",
                energy=0.1,
                effects = [
                    Distorter(vect_fun=down),
                    RandomDrawer(period=1, particles=10, color=AnimatedHSVColor(h=ConstantValue(0.6), s=ConstantValue(1))),
                ]),
            Visualization(name="Shuffle 1", min_bpm=30, max_bpm=180,
                energy=0.8,
                effects = [
                    portalOut,
                    Animation(npy_path="resources/animations/shuffle1.npy", driver=AnimatedValue(fun1=lambda x:1-x), color=AnimatedHSVColor(v=ConstantValue(1))),
                    Distorter(vect_fun=from_center, darken=0.2),
                    portalIn,
                    Animation(npy_path="resources/animations/shuffle1.npy", driver=AnimatedValue(fun1=lambda x:1-x), color=AnimatedHSVColor(h=ConstantValue(1), s=ConstantValue(0), v=ConstantValue(1))),
                ]),
            Visualization(name="Shuffle 2", min_bpm=30, max_bpm=180,
                energy=0.8,
                effects = [
                    portalOut,
                    Animation(npy_path="resources/animations/shuffle2-2.npy", driver=AnimatedValue(fun1=lambda x:1-x, period=2), color=AnimatedHSVColor(v=ConstantValue(1))),
                    Distorter(vect_fun=from_center, darken=0.2),
                    portalIn,
                    Animation(npy_path="resources/animations/shuffle2-2.npy", driver=AnimatedValue(fun1=lambda x:1-x, period=2), color=AnimatedHSVColor(h=ConstantValue(1), s=ConstantValue(0), v=ConstantValue(1))),
                ]),
            Visualization(name="Shuffle 3", min_bpm=30, max_bpm=180,
                energy=0.8,
                effects = [
                    portalOut,
                    Animation(npy_path="resources/animations/shuffle3.npy", driver=AnimatedValue(fun1=lambda x:1-x, period=2), color=AnimatedHSVColor(v=ConstantValue(1))),
                    Distorter(vect_fun=from_center, darken=0.2),
                    portalIn,
                    Animation(npy_path="resources/animations/shuffle3.npy", driver=AnimatedValue(fun1=lambda x:1-x, period=2), color=AnimatedHSVColor(h=ConstantValue(1), s=ConstantValue(0), v=ConstantValue(1))),
                ]),
            Visualization(name="Game of Life",
                effects = [
                    Distorter(vect_fun=to_center, darken=0.5),
                    GameOfLife(),
                ]),
            Visualization(name="Color Wave", max_bpm=180,
                energy=0.4,
                effects=[
                    Distorter(vect_fun=from_center ),
                    Drawer(color=AnimatedHSVColor()),
                ]),
        ]
        self.visualization_index = len(self.visualizations) - 1

    def next_visualization(self):
        bpm = 60 / self.beat_duration
        probabilities = [vis.is_fitting(bpm, self.energy) for vis in self.visualizations]
        idx = random.choices(range(len(self.visualizations)), weights=probabilities)[0]
        print(f"Chosen {self.visualizations[idx].name}")
        self.visualization_index = idx
        self.last_change = self.beat_count


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
            self.next_visualization()

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
        if self.beat:
            self.beat_count += 1
        
        beats_since_change = self.beat_count - self.last_change
        if beats_since_change != 0 and beats_since_change % 16 == 0:
            self.next_visualization()

        print(f"\r{60/self.beat_duration:.2f} BPM ({self.beat_duration:.2f} s)", end="    ")
        progression = (now - self.last_beats[0]) / self.beat_duration
        viz = self.visualizations[self.visualization_index]
        self.last_frame = viz.apply(self.last_frame, delta, progression, self.beat)
        io.display.pixels = self.last_frame
