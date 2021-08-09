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
    def __init__(self, effects=[], energy=0.5):
        self.effects = effects
        self.energy = energy
    
    def apply(self, frame, delta, progression, beat):
        for effect in self.effects:
            frame = effect.apply(frame, delta, progression, beat)
        return frame

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
        self.beat = False
        self.last_click = now
        self.last_beats = [now - i*self.beat_duration for i in range(self.BEAT_MEMORY_SIZE)]
        
        center = [(self.SIZE[0]//2, self.SIZE[1]//2)]

        edge = [(x, 0) for x in range(self.SIZE[0])] + \
                 [(self.SIZE[0]-1, y) for y in range(1, self.SIZE[1])] + \
                 [(x, self.SIZE[1]-1) for x in range(self.SIZE[0]-2, 0,-1)] + \
                 [(0, y) for y in range(self.SIZE[1]-1,0,-1)]

        circle_big = [(3, 2), (4, 2), (5, 2), (6, 2), (7, 3), (8, 4), (9, 5), (9, 6), (9, 7), (9, 8), (8, 9), (7, 10), (6, 11), (5, 11), (4, 11), (3, 11), (2, 10), (1, 9), (0, 8), (0, 7), (0, 6), (0, 5), (1, 4), (2, 3)]
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
            Visualization([
                Distorter(),
                Drawer(coords=edge, color=AnimatedHSVColor()),
            ]),
            Visualization([
                Distorter(vect_fun=swirl),
                RandomDrawer(period=1),
            ]),
            Visualization([
                Distorter(vect_fun=to_center),
                Particles(path=edge, particles=5, radius=3, position=AnimatedValue(period=8)),
            ]),
            Visualization([
                Distorter(vect_fun=from_center),
                RandomDrawer(period=1, particles=50, color=AnimatedHSVColor(h=ConstantValue(0), s=ConstantValue(0), v=AnimatedValue(fun1=lambda x:0 if x < 0.1 else 1))),
            ]),
            Visualization([
                Distorter(vect_fun=up),
                Particles(path=all_coords, particles=16, position=AnimatedValue(period=50)),
            ]),
            Visualization([
                Distorter(vect_fun=down),
                RandomDrawer(period=1, particles=10, color=AnimatedHSVColor(h=ConstantValue(0.6), s=ConstantValue(1))),
            ]),
            Visualization([
                portalOut,
                Animation(npy_path="resources/animations/shuffle1.npy", driver=AnimatedValue(fun1=lambda x:1-x), color=AnimatedHSVColor(v=ConstantValue(1))),
                Distorter(vect_fun=from_center, darken=0.2),
                portalIn,
                Animation(npy_path="resources/animations/shuffle1.npy", driver=AnimatedValue(fun1=lambda x:1-x), color=AnimatedHSVColor(h=ConstantValue(1), s=ConstantValue(0), v=ConstantValue(1))),
            ]),
            Visualization([
                portalOut,
                Animation(npy_path="resources/animations/shuffle2-2.npy", driver=AnimatedValue(fun1=lambda x:1-x, period=2), color=AnimatedHSVColor(v=ConstantValue(1))),
                Distorter(vect_fun=from_center, darken=0.2),
                portalIn,
                Animation(npy_path="resources/animations/shuffle2-2.npy", driver=AnimatedValue(fun1=lambda x:1-x, period=2), color=AnimatedHSVColor(h=ConstantValue(1), s=ConstantValue(0), v=ConstantValue(1))),
            ]),
            Visualization([
                portalOut,
                Animation(npy_path="resources/animations/shuffle3.npy", driver=AnimatedValue(fun1=lambda x:1-x, period=2), color=AnimatedHSVColor(v=ConstantValue(1))),
                Distorter(vect_fun=from_center, darken=0.2),
                portalIn,
                Animation(npy_path="resources/animations/shuffle3.npy", driver=AnimatedValue(fun1=lambda x:1-x, period=2), color=AnimatedHSVColor(h=ConstantValue(1), s=ConstantValue(0), v=ConstantValue(1))),
            ]),

        ]
        """
        # Visualizations
        self.visualizations = [
            Visualization(
                ColorBlinker(shape, coords = center),
                Wave(shape, pred=from_center)),
            Visualization(
                Blinker2(shape, coords = center, fun=lambda x:(1-x)**4),
                Wave(shape, pred=from_center)),
            Visualization(
                Particles(shape, path=circle_big, n_particles=2, radius=2, speed=-1, fun=lambda x:1-(0.1+0.9*x)**2),
                Wave(shape, pred=to_center, speed=2)),
            Visualization(
                Particles(shape, path=circle_small, n_particles=2, radius=1, speed=0.5),
                Wave(shape, pred=from_center, speed=1)),
            Visualization(
                Animation("resources/animations/shuffle1.npy", shape, fun=lambda x:(0.5+0.5*(1-x))**2),
                Wave(shape, pred=from_center, darken=0.4, speed=1)),
            Visualization(
                Animation("resources/animations/shuffle2.npy", shape, animation_cycle=2, fun=lambda x:(0.5+0.5*(1-x))**2),
                Wave(shape, pred=from_center, darken=0.4, speed=1)),
            Visualization(
                Animation("resources/animations/shuffle3.npy", shape, animation_cycle=2, fun=lambda x:(0.5+0.5*(1-x))**2),
                Wave(shape, pred=from_center, darken=0.4, speed=1)),
            Visualization(
                RandomBlinker(Blinker2(shape, color=Color(255, 100, 0)), n_active=10, change_interval=1),
                Wave(shape, pred=up_wave, speed=4)),

        ]
        """
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
        self.last_frame = viz.apply(self.last_frame, delta, progression, self.beat)
        io.display.pixels = self.last_frame
