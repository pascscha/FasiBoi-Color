from applications import core
from applications.games.maze import MazeUtils
from helpers import bitmaputils, textutils
from IO.color import *
import time
import random
import math
import cv2


class MilkdropValue:
    def get_value(self, delta, progression, beat):
        raise NotImplementedError("Please Implement this method!")


class ConstantValue(MilkdropValue):
    def __init__(self, value):
        self.value = value

    def get_value(self, delta, progression, beat):
        return self.value


class AnimatedValue(MilkdropValue):
    def __init__(
        self,
        *args,
        fun1=lambda x: x**2,
        fun2=lambda x: 1 - x,
        period=1,
        offset=0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.beat_count = 0
        self.fun1 = fun1
        self.fun2 = fun2
        self.period = period
        self.offset = offset

    def get_value(self, delta, progression, beat):
        if beat:
            self.beat_count = (self.beat_count + 1) % self.period
        return self.fun2((self.beat_count + self.fun1(progression)) / self.period)


class AnimatedHSVColor:
    def __init__(
        self,
        *args,
        h: MilkdropValue = AnimatedValue(period=8),
        s: MilkdropValue = ConstantValue(1),
        v: MilkdropValue = AnimatedValue(),
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.h = h
        self.s = s
        self.v = v

    def get_value(self, delta, progression, beat):
        return Color.from_hsv(
            self.h.get_value(delta, progression, beat),
            self.s.get_value(delta, progression, beat),
            self.v.get_value(delta, progression, beat),
        )


class Content:
    def apply(self, frame, delta, progression, beat):
        raise NotImplementedError()


class Drawer(Content):
    def __init__(self, color=AnimatedHSVColor(), coords=None, radius=1):
        if coords is None:
            coords = [(5, 7)]
        self.color = color
        self.coords = coords
        self.radius = radius
        self.radius1 = math.floor(radius / 2)
        self.radius2 = math.ceil(radius / 2)

    def apply(self, frame, delta, progression, beat):
        color = self.color.get_value(delta, progression, beat)
        for x, y in self.coords:
            frame[
                max(0, x - self.radius1) : min(frame.shape[0], x + self.radius2),
                max(0, y - self.radius1) : min(frame.shape[1], y + self.radius2),
            ] = color
        return frame


class RandomDrawer(Drawer):
    def __init__(self, *args, coords=None, period=4, particles=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = period
        self.particles = particles
        self.beat_count = 0

    def apply(self, frame, delta, progression, beat):
        if beat or self.beat_count == 0:
            self.beat_count += 1
            if self.beat_count % self.period == 0:
                self.coords = [
                    (
                        random.randint(0, frame.shape[0] - 1),
                        random.randint(0, frame.shape[1] - 1),
                    )
                    for _ in range(self.particles)
                ]
        return super().apply(frame, delta, progression, beat)


class Particles(Drawer):
    def __init__(
        self, *args, path=None, particles=10, position=AnimatedValue(period=4), **kwargs
    ):
        super().__init__(*args, **kwargs)
        if path is None:
            path = [(5, 7)]
        self.path = path
        self.particles = particles
        self.position = position

    def apply(self, frame, delta, progression, beat):
        pos = self.position.get_value(delta, progression, beat)
        self.coords = [
            self.path[int((pos + i / self.particles) * len(self.path)) % len(self.path)]
            for i in range(self.particles)
        ]
        return super().apply(frame, delta, progression, beat)


class Animation(Drawer):
    def __init__(
        self, *args, driver=AnimatedValue(fun1=lambda x: x), path=None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        if path.endswith(".npy"):
            animation = np.load(path)
            self.frame_coords = [
                list(zip(*reversed(np.where(frame)))) for frame in animation
            ]
        elif path.endswith(".gif"):
            self.frame_coords = []
            cap = cv2.VideoCapture(path)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret == True:
                    self.frame_coords.append(
                        list(zip(*reversed(np.where(frame[:, :, 0] == 255))))
                    )
                else:
                    break
            cap.release()
        else:
            raise ValueError(f"Cannot load animations of type {path.split('.')[-1]}")

        self.animation_length = len(self.frame_coords)
        self.driver = driver

    def apply(self, frame, delta, progression, beat):
        idx = int(
            self.driver.get_value(delta, progression, beat) * self.animation_length
        )
        self.coords = self.frame_coords[idx % self.animation_length]
        return super().apply(frame, delta, progression, beat)


class TextDrawer(Drawer):
    def __init__(
        self,
        *args,
        text="PARTY!!!",
        loc=(4, 5),
        driver=AnimatedValue(fun2=lambda x: x, period=8),
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.loc = np.array(loc)
        bitmaps = [textutils.get_char_bitmap(c) for c in text]
        unmoved_coords = [list(zip(*reversed(np.where(bmp)))) for bmp in bitmaps]
        self.frame_coords = [
            self.loc + np.array(c) if len(c) > 0 else c for c in unmoved_coords
        ]
        self.animation_length = len(self.frame_coords)
        self.driver = driver

    def apply(self, frame, delta, progression, beat):
        idx = int(
            self.driver.get_value(delta, progression, beat) * self.animation_length
        )
        self.coords = self.frame_coords[idx % self.animation_length]
        return super().apply(frame, delta, progression, beat)


class GameOfLife(Drawer):
    def __init__(self, *args, period=128, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = None
        self.period = period
        self.beat_count = 0

    @staticmethod
    def get(field, x, y):
        return field[x % field.shape[0], y % field.shape[1]]

    def apply(self, frame, delta, progression, beat):
        if beat:
            self.beat_count = (self.beat_count + 1) % self.period
            if self.beat_count == 0:
                self.field = None

        if self.field is None or np.all(self.field == False):
            self.field = np.zeros(frame.shape[:2], dtype=np.uint8)
            for i in range(frame.shape[0] * frame.shape[1] // 2):
                x = random.randint(0, frame.shape[0] - 1)
                y = random.randint(0, frame.shape[1] - 1)
                self.field[x][y] = True

        if beat:
            next_field = np.zeros(self.field.shape)
            for x in range(next_field.shape[0]):
                for y in range(next_field.shape[1]):
                    count = (
                        0
                        + self.get(self.field, x - 1, y - 1)
                        + self.get(self.field, x - 1, y)
                        + self.get(self.field, x - 1, y + 1)
                        + self.get(self.field, x, y - 1)
                        + self.get(self.field, x, y + 1)
                        + self.get(self.field, x + 1, y - 1)
                        + self.get(self.field, x + 1, y)
                        + self.get(self.field, x + 1, y + 1)
                    )
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


class Maze(Content):
    def __init__(
        self,
        background_color=AnimatedHSVColor(),
        color1=AnimatedHSVColor(v=ConstantValue(0)),
        color2=AnimatedHSVColor(s=ConstantValue(0), v=ConstantValue(1)),
    ):
        self.beat_count = 0
        self.maze = None
        self.distances1 = None
        self.distances2 = None

        self.background_color = background_color
        self.color1 = color1
        self.color2 = color2

        self.max1 = 0
        self.max2 = 0

    def apply(self, frame, delta, progression, beat):
        if beat:
            self.beat_count += 1

        if beat and self.beat_count % 4 == 0 or self.maze is None:
            self.maze, (self.distances1, self.distances2) = MazeUtils.generate_maze(
                *frame.shape[:2]
            )
            self.max1 = max(
                [d for row in self.distances1 for d in row if d != MazeUtils.INFINITY]
            )
            self.max2 = max(
                [d for row in self.distances2 for d in row if d != MazeUtils.INFINITY]
            )

            center = None
            for x in range(frame.shape[0]):
                if center is None:
                    for y in range(frame.shape[1]):
                        if (
                            self.maze.get_value(x, y) == self.maze.COLOR1
                            and self.distances1[x][y] == MazeUtils.INFINITY
                            and self.distances2[x][y] == MazeUtils.INFINITY
                        ):
                            center = (x, y)
                            break
            self.path = [center]

            p1 = center
            while p1[1] != 0:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if (
                        self.distances1[p1[0] + dx][p1[1] + dy]
                        < self.distances1[p1[0]][p1[1]]
                    ):
                        p1 = (p1[0] + dx, p1[1] + dy)
                        self.path.append(p1)

            p2 = center
            while p2[1] != frame.shape[1] - 1:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if (
                        self.distances2[p2[0] + dx][p2[1] + dy]
                        < self.distances2[p2[0]][p2[1]]
                    ):
                        p2 = (p2[0] + dx, p2[1] + dy)
                        self.path.append(p2)

        bg = self.background_color.get_value(delta, progression, beat)
        # frame[:,:] = (0,0,0)
        c1 = self.color1.get_value(delta, progression, beat)
        c2 = self.color2.get_value(delta, progression, beat)

        if self.beat_count % 2 == 0:
            max_distance1 = self.max1 * progression + 1
            max_distance2 = self.max2 * progression + 1

            for x in range(frame.shape[0]):
                for y in range(frame.shape[1]):
                    if (
                        self.distances1[x][y] != MazeUtils.INFINITY
                        and self.distances1[x][y] < max_distance1
                    ):
                        frame[x][y] = bg * (self.distances1[x][y] / max_distance1)
                    elif (
                        self.distances2[x][y] != MazeUtils.INFINITY
                        and self.distances2[x][y] < max_distance2
                    ):
                        frame[x][y] = bg * (self.distances2[x][y] / max_distance2)

        else:
            for x in range(frame.shape[0]):
                for y in range(frame.shape[1]):
                    if self.distances1[x][y] != MazeUtils.INFINITY:
                        frame[x][y] = bg * (0.2)  # * self.distances1[x][y] / self.max1)
                    if self.distances2[x][y] != MazeUtils.INFINITY:
                        frame[x][y] = bg * (0.2)  # * self.distances2[x][y] / self.max2)
            for x, y in self.path:
                frame[x][y] = bg

        return frame


def down(w, h, x, y):
    return (0, -1)


def up(w, h, x, y):
    return (0, 1)


def up_wave(w, h, x, y):
    return (y % 3 - 1, 1)


def to_center(w, h, x, y):
    return -(w / 2 - x), -(h / 2 - y)


def from_center(w, h, x, y):
    return (w / 2 - x), (h / 2 - y)


def swirl(w, h, x, y):
    return h / 2 - y, x - w / 2


def swirl2(w, h, x, y, f=0.7):
    tx = (w / 2 - x) / 2
    ty = (h / 2 - y) / 2
    return ty * f - tx * (1 - f), -tx * f - ty * (1 - f)


class Distorter(Content):
    def __init__(self, shape=(10, 15), speed=6, vect_fun=to_center, darken=0.1):
        self.speed = speed
        self.shape = shape

        # Calculate weights
        weights = np.zeros(shape=(9, *shape), dtype=np.float32)
        for x in range(shape[0]):
            for y in range(shape[1]):
                vector = np.array(vect_fun(*shape, x, y))
                norm = np.linalg.norm(vector)
                if norm > 1:
                    vector = vector / norm
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        weights[(i + 1) * 3 + j, x, y] += np.linalg.norm(
                            -vector + (i, j)
                        )

        # weights = np.eye(9)[np.argmin(weights, axis=0)]

        # only look at points closer than sqrt(2)
        weights = 1.42 - weights
        weights[np.where(weights < 0)] = 0

        # make sure sum of weights is 0
        weights = weights / np.sum(weights, axis=0)

        # weights = np.max(weights, axis=0) - weights
        # weights = weights / np.sum(weights, axis=0)

        self.weights = []

        for x in range(-1, 2):
            for y in range(-1, 2):
                w = weights[(x + 1) * 3 + y]
                if x == -1:
                    w[1, :] += w[0, :]
                    w = w[1:]
                    range_x1 = (1, shape[0])
                    range_x2 = (0, shape[0] - 1)
                elif x == 0:
                    range_x1 = (0, shape[0])
                    range_x2 = (0, shape[0])
                elif x == 1:
                    w[-2, :] += w[-1, :]
                    w = w[:-1]
                    range_x1 = (0, shape[0] - 1)
                    range_x2 = (1, shape[0])

                if y == -1:
                    w[:, 1] += w[:, 0]
                    w = w[:, 1:]
                    range_y1 = (1, shape[1])
                    range_y2 = (0, shape[1] - 1)
                elif y == 0:
                    range_y1 = (0, shape[1])
                    range_y2 = (0, shape[1])
                elif y == 1:
                    w[:, -2] += w[:, -1]
                    w = w[:, :-1]
                    range_y1 = (0, shape[1] - 1)
                    range_y2 = (1, shape[1])
                self.weights.append(
                    (range_x1, range_x2, range_y1, range_y2, w.reshape(*w.shape, 1))
                )

        self.vectors = [
            [vect_fun(*shape, x, y) for y in range(shape[1])] for x in range(shape[0])
        ]
        self.darken = darken

    def apply(self, frame, delta, progression, beat):
        darkened = frame * (1 - self.darken)
        out = np.zeros(darkened.shape, dtype=np.float32)

        for range_x1, range_x2, range_y1, range_y2, weights in self.weights:
            out[range_x1[0] : range_x1[1], range_y1[0] : range_y1[1]] += (
                weights * darkened[range_x2[0] : range_x2[1], range_y2[0] : range_y2[1]]
            )

        out[np.where(out > 255)] = 255
        out[np.where(out < 0)] = 0

        return out.astype(np.uint8)


class Visualization:
    REPEAT_TIME = 30

    def __init__(self, effects=None, name=None, min_bpm=None, max_bpm=None, energy=0.5):
        if effects is None:
            effects = []
        self.name = name
        self.effects = effects
        self.min_bpm = min_bpm
        self.max_bpm = max_bpm
        self.energy = energy
        self.last_applied = time.time() - self.REPEAT_TIME

    def apply(self, frame, delta, progression, beat):
        self.last_applied = time.time()
        for effect in self.effects:
            frame = effect.apply(frame, delta, progression, beat)
        return frame

    @staticmethod
    def gaussian(x, height=1.0, center=0.0, deviation=1.0):
        return height * math.exp(-((x - center) ** 2) / (2 * deviation**2))

    def is_fitting(self, bpm, energy):
        if self.min_bpm is not None and bpm < self.min_bpm:
            return 0
        elif self.max_bpm is not None and bpm > self.max_bpm:
            return 0

        now = time.time()
        energy_fit = self.gaussian(self.energy, center=energy, deviation=0.3)
        time_fit = 1 - self.gaussian(
            now, center=self.last_applied, deviation=self.REPEAT_TIME
        )
        # print(
        #     f"{str(self.name):>20} {energy_fit * time_fit:.2f} (e: {energy_fit:.2f}, t: {time_fit:.2f})"
        # )
        return energy_fit * time_fit


class FrameHolder:
    def __init__(self):
        self.frame = None


class PortalIn(Content):
    def __init__(self, frame_holder):
        self.frameHolder = frame_holder

    def apply(self, frame, delta, progression, beat):
        self.frameHolder.frame = frame.copy()
        return frame


class PortalOut(Content):
    def __init__(self, frame_holder):
        self.frameHolder = frame_holder

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
        self.reset()

    def reset(self):
        self.beat_duration = 0.5
        self.energy = 0.5
        now = time.time()
        self.last = now
        self.beat_count = 0
        self.last_change = 0
        self.beat = False
        self.last_click = now
        self.last_beats = [
            now - i * self.beat_duration for i in range(self.BEAT_MEMORY_SIZE)
        ]

        center = [(self.SIZE[0] // 2, self.SIZE[1] // 2)]

        edge = (
            [(x, 0) for x in range(self.SIZE[0])]
            + [(self.SIZE[0] - 1, y) for y in range(1, self.SIZE[1])]
            + [(x, self.SIZE[1] - 1) for x in range(self.SIZE[0] - 2, 0, -1)]
            + [(0, y) for y in range(self.SIZE[1] - 1, 0, -1)]
        )

        circle_big = [
            (3, 3),
            (4, 3),
            (5, 3),
            (6, 3),
            (7, 4),
            (8, 5),
            (9, 6),
            (9, 7),
            (9, 8),
            (9, 9),
            (8, 10),
            (7, 11),
            (6, 12),
            (5, 12),
            (4, 12),
            (3, 12),
            (2, 11),
            (1, 10),
            (0, 9),
            (0, 8),
            (0, 7),
            (0, 6),
            (1, 5),
            (2, 4),
        ]
        circle_medium = [
            (4, 5),
            (5, 5),
            (6, 6),
            (7, 7),
            (7, 8),
            (6, 9),
            (5, 10),
            (4, 10),
            (3, 9),
            (2, 8),
            (2, 7),
            (3, 6),
        ]
        circle_small = [(4, 6), (5, 6), (6, 7), (6, 8), (5, 9), (4, 9), (3, 8), (3, 7)]

        all_coords = [(x, y) for x in range(self.SIZE[0]) for y in range(self.SIZE[1])]
        shape = (*self.SIZE, 3)
        self.last_frame = np.zeros(shape)

        frame_holder = FrameHolder()
        portal_in = PortalIn(frame_holder)
        portal_out = PortalOut(frame_holder)

        # Visualizations
        self.visualizations = [
            Visualization(
                name="Tunnel",
                energy=0.8,
                effects=[
                    Distorter(),
                    Drawer(coords=edge, color=AnimatedHSVColor()),
                ],
            ),
            Visualization(
                name="Galaxy",
                max_bpm=200,
                energy=0.2,
                effects=[
                    Distorter(vect_fun=swirl, darken=0),
                    RandomDrawer(period=1),
                ],
            ),
            Visualization(
                name="Stage Lights",
                energy=0.6,
                effects=[
                    Distorter(vect_fun=to_center),
                    Particles(
                        path=edge,
                        particles=5,
                        radius=3,
                        position=AnimatedValue(period=8),
                    ),
                ],
            ),
            # Visualization(
            #     name="Thunderstorm",
            #     energy=1,
            #     effects=[
            #         Distorter(vect_fun=from_center),
            #         RandomDrawer(
            #             period=1,
            #             particles=50,
            #             color=AnimatedHSVColor(
            #                 h=ConstantValue(0),
            #                 s=ConstantValue(0),
            #                 v=AnimatedValue(fun1=lambda x: 0 if x < 0.1 else 1),
            #             ),
            #         ),
            #     ],
            # ),
            Visualization(
                name="Woven Colors",
                energy=0.2,
                effects=[
                    Distorter(vect_fun=up),
                    Particles(
                        path=all_coords, particles=16, position=AnimatedValue(period=50)
                    ),
                ],
            ),
            Visualization(
                name="Rain",
                energy=0.1,
                effects=[
                    Distorter(vect_fun=down),
                    RandomDrawer(
                        period=1,
                        particles=10,
                        color=AnimatedHSVColor(
                            h=ConstantValue(0.6), s=ConstantValue(1)
                        ),
                    ),
                ],
            ),
            Visualization(
                name="Shuffle 1",
                min_bpm=30,
                max_bpm=180,
                energy=0.8,
                effects=[
                    portal_out,
                    Animation(
                        path="resources/animations/shuffle1.npy",
                        driver=AnimatedValue(fun1=lambda x: 1 - x),
                        color=AnimatedHSVColor(v=ConstantValue(1)),
                    ),
                    Distorter(vect_fun=from_center, darken=0.2),
                    portal_in,
                    Animation(
                        path="resources/animations/shuffle1.npy",
                        driver=AnimatedValue(fun1=lambda x: 1 - x),
                        color=AnimatedHSVColor(
                            h=ConstantValue(1), s=ConstantValue(0), v=ConstantValue(1)
                        ),
                    ),
                ],
            ),
            Visualization(
                name="Shuffle 2",
                min_bpm=30,
                max_bpm=180,
                energy=0.8,
                effects=[
                    portal_out,
                    Animation(
                        path="resources/animations/shuffle2-2.npy",
                        driver=AnimatedValue(fun1=lambda x: 1 - x, period=2),
                        color=AnimatedHSVColor(v=ConstantValue(1)),
                    ),
                    Distorter(vect_fun=from_center, darken=0.2),
                    portal_in,
                    Animation(
                        path="resources/animations/shuffle2-2.npy",
                        driver=AnimatedValue(fun1=lambda x: 1 - x, period=2),
                        color=AnimatedHSVColor(
                            h=ConstantValue(1), s=ConstantValue(0), v=ConstantValue(1)
                        ),
                    ),
                ],
            ),
            Visualization(
                name="Shuffle 3",
                min_bpm=30,
                max_bpm=180,
                energy=0.8,
                effects=[
                    portal_out,
                    Animation(
                        path="resources/animations/shuffle3.npy",
                        driver=AnimatedValue(fun1=lambda x: 1 - x, period=2),
                        color=AnimatedHSVColor(v=ConstantValue(1)),
                    ),
                    Distorter(vect_fun=from_center, darken=0.2),
                    portal_in,
                    Animation(
                        path="resources/animations/shuffle3.npy",
                        driver=AnimatedValue(fun1=lambda x: 1 - x, period=2),
                        color=AnimatedHSVColor(
                            h=ConstantValue(1), s=ConstantValue(0), v=ConstantValue(1)
                        ),
                    ),
                ],
            ),
            Visualization(
                name="Game of Life",
                effects=[
                    Distorter(vect_fun=to_center, darken=0.5),
                    GameOfLife(),
                ],
            ),
            Visualization(
                name="Color Wave",
                max_bpm=180,
                energy=0.4,
                effects=[
                    Distorter(vect_fun=from_center, darken=0),
                    Drawer(color=AnimatedHSVColor(h=AnimatedValue(period=8))),
                ],
            ),
            Visualization(
                name="PARTY!!!",
                energy=0.8,
                effects=[Distorter(vect_fun=from_center, darken=0.4), TextDrawer()],
            ),
            Visualization(
                name="FASNACHT",
                energy=0.3,
                effects=[
                    Distorter(vect_fun=from_center, darken=0.45),
                    TextDrawer(
                        text="FASNACHT",
                        loc=(2, 5),
                        driver=AnimatedValue(fun2=lambda x: x, period=8),
                        color=AnimatedHSVColor(h=ConstantValue(0.66)),
                    ),
                    TextDrawer(
                        text="FASNACHT",
                        loc=(5, 5),
                        driver=AnimatedValue(fun2=lambda x: x, period=8),
                        color=AnimatedHSVColor(s=ConstantValue(0)),
                    ),
                ],
            ),
            Visualization(
                name="UNZ",
                min_bpm=100,
                energy=0.9,
                effects=[
                    Distorter(vect_fun=from_center),
                    Distorter(vect_fun=to_center),
                    Distorter(vect_fun=swirl2, darken=0.2),
                    TextDrawer(
                        text="U  ",
                        loc=(0, 0),
                        driver=AnimatedValue(fun2=lambda x: x, period=3),
                        color=AnimatedHSVColor(
                            h=AnimatedValue(
                                fun2=lambda x: x - 0.5 if x > 0.5 else x + 0.5, period=8
                            ),
                            v=AnimatedValue(fun1=lambda x: x / 2),
                        ),
                    ),
                    TextDrawer(
                        text="N  ",
                        loc=(3, 0),
                        driver=AnimatedValue(fun2=lambda x: x, period=3),
                        color=AnimatedHSVColor(
                            h=AnimatedValue(period=8),
                            v=AnimatedValue(fun1=lambda x: x / 2),
                        ),
                    ),
                    TextDrawer(
                        text="Z  ",
                        loc=(6, 0),
                        driver=AnimatedValue(fun2=lambda x: x, period=3),
                        color=AnimatedHSVColor(
                            h=AnimatedValue(
                                fun2=lambda x: x - 0.5 if x > 0.5 else x + 0.5, period=8
                            ),
                            v=AnimatedValue(fun1=lambda x: x / 2),
                        ),
                    ),
                    TextDrawer(
                        text=" U ",
                        loc=(0, 5),
                        driver=AnimatedValue(fun2=lambda x: x, period=3),
                        color=AnimatedHSVColor(
                            h=AnimatedValue(
                                fun2=lambda x: x - 0.5 if x > 0.5 else x + 0.5, period=8
                            ),
                            v=AnimatedValue(fun1=lambda x: x / 2),
                        ),
                    ),
                    TextDrawer(
                        text=" N ",
                        loc=(3, 5),
                        driver=AnimatedValue(fun2=lambda x: x, period=3),
                        color=AnimatedHSVColor(
                            h=AnimatedValue(period=8),
                            v=AnimatedValue(fun1=lambda x: x / 2),
                        ),
                    ),
                    TextDrawer(
                        text=" Z ",
                        loc=(6, 5),
                        driver=AnimatedValue(fun2=lambda x: x, period=3),
                        color=AnimatedHSVColor(
                            h=AnimatedValue(
                                fun2=lambda x: x - 0.5 if x > 0.5 else x + 0.5, period=8
                            ),
                            v=AnimatedValue(fun1=lambda x: x / 2),
                        ),
                    ),
                    TextDrawer(
                        text="  U",
                        loc=(0, 10),
                        driver=AnimatedValue(fun2=lambda x: x, period=3),
                        color=AnimatedHSVColor(
                            h=AnimatedValue(period=8),
                            v=AnimatedValue(fun1=lambda x: x / 2),
                        ),
                    ),
                    TextDrawer(
                        text="  N",
                        loc=(3, 10),
                        driver=AnimatedValue(fun2=lambda x: x, period=3),
                        color=AnimatedHSVColor(
                            h=AnimatedValue(
                                fun2=lambda x: x - 0.5 if x > 0.5 else x + 0.5, period=8
                            ),
                            v=AnimatedValue(fun1=lambda x: x / 2),
                        ),
                    ),
                    TextDrawer(
                        text="  Z",
                        loc=(6, 10),
                        driver=AnimatedValue(fun2=lambda x: x, period=3),
                        color=AnimatedHSVColor(
                            h=AnimatedValue(period=8),
                            v=AnimatedValue(fun1=lambda x: x / 2),
                        ),
                    ),
                ],
            ),
            Visualization(name="maze", effects=[Distorter(darken=1), Maze()]),
            Visualization(
                name="Fireworks",
                min_bpm=30,
                max_bpm=180,
                energy=0.8,
                effects=[
                    Distorter(vect_fun=down, darken=0.5),
                    Animation(
                        path="resources/animations/fireworks.gif",
                        driver=AnimatedValue(fun1=lambda x: 1 - x, period=2),
                        color=AnimatedHSVColor(v=ConstantValue(1)),
                    ),
                ],
            ),
            Visualization(
                name="Heart",
                min_bpm=30,
                max_bpm=180,
                energy=0.8,
                effects=[
                    Distorter(vect_fun=from_center, darken=0.5),
                    Animation(
                        path="resources/animations/heart.gif",
                        driver=AnimatedValue(fun1=lambda x: 1 - x, period=2),
                        color=AnimatedHSVColor(
                            h=ConstantValue(0),
                            v=AnimatedValue(fun2=lambda x: 1 - x / 2, period=2),
                        ),
                    ),
                ],
            ),
            Visualization(
                name="Worms",
                min_bpm=30,
                max_bpm=180,
                energy=0.8,
                effects=[
                    Distorter(vect_fun=to_center, darken=0.5),
                    Animation(
                        path="resources/animations/worms.gif",
                        driver=AnimatedValue(fun1=lambda x: 1 - x, period=2),
                        color=AnimatedHSVColor(
                            v=ConstantValue(1),
                            h=ConstantValue(0.66),
                            s=AnimatedValue(
                                fun1=lambda x: x, fun2=lambda x: 0 if x > 0.5 else 1
                            ),
                        ),
                    ),
                ],
            ),
            Visualization(
                name="Sound_Wave",
                min_bpm=30,
                max_bpm=180,
                energy=0.8,
                effects=[
                    Distorter(vect_fun=to_center, darken=0.5),
                    Animation(
                        path="resources/animations/sound_wave.gif",
                        driver=AnimatedValue(fun1=lambda x: 1 - x, period=2),
                        color=AnimatedHSVColor(
                            v=ConstantValue(1),
                            h=AnimatedValue(fun2=lambda x: (1 - x) / 6, period=2),
                        ),
                    ),
                ],
            ),
        ]
        self.visualization_index = len(self.visualizations) - 1

    def next_visualization(self):
        bpm = 60 / self.beat_duration
        probabilities = [
            vis.is_fitting(bpm, self.energy) for vis in self.visualizations
        ]
        idx = random.choices(range(len(self.visualizations)), weights=probabilities)[0]
        # print(f"Chosen {self.visualizations[idx].name}")
        self.visualization_index = idx
        self.last_change = self.beat_count

    def update(self, io, delta):
        now = time.time()
        if now - self.last > 10 * delta:
            self.reset()

        if io.controller.button_up.fresh_press():
            self.energy = min(1.0, self.energy + 1 / self.ENERGY_GRANULARITY)

        if io.controller.button_down.fresh_press():
            self.energy = max(0.0, self.energy - 1 / self.ENERGY_GRANULARITY)

        if io.controller.button_right.fresh_press():
            self.last_change = self.beat_count
            self.visualization_index = (self.visualization_index + 1) % len(
                self.visualizations
            )

        if io.controller.button_left.fresh_press():
            self.last_change = self.beat_count
            self.visualization_index = (self.visualization_index - 1) % len(
                self.visualizations
            )

        if io.controller.button_b.fresh_press():
            self.next_visualization()

        if io.controller.button_a.fresh_press():
            self.last_change = self.beat_count
            click_duration = now - self.last_click
            # Check if last click was recently
            if click_duration < 10:
                # If Clicking and beat roughly at the same speed, just correct
                if 0.75 < click_duration / self.beat_duration < 1.33:

                    diff1 = abs(now - (self.last_beats[0] + self.beat_duration))
                    diff2 = abs(now - self.last_beats[0])
                    if diff1 > diff2:
                        # Slightly slower that the current beat, correct
                        # current beat
                        self.last_beats[0] = now
                    else:
                        # Slightly faster that the current beat, add new beat
                        # now
                        self.beat = True
                        self.last_beats = [now] + self.last_beats[
                            : self.BEAT_MEMORY_SIZE - 1
                        ]
                    self.beat_duration = (self.last_beats[0] - self.last_beats[-1]) / (
                        len(self.last_beats) - 1
                    )
                else:
                    # Clicking and beat drastically different speeds, change
                    # tempo
                    self.beat_duration = click_duration
                    self.beat = True
                    self.last_beats = [
                        now - i * self.beat_duration
                        for i in range(self.BEAT_MEMORY_SIZE)
                    ]
            self.last_click = now
        else:
            if self.last_beats[0] + self.beat_duration < now:
                self.beat = True
                self.last_beats = [
                    self.last_beats[0] + self.beat_duration
                ] + self.last_beats[: self.BEAT_MEMORY_SIZE - 1]
            else:
                self.beat = False
        if self.beat:
            self.beat_count += 1

        # print(60 / self.beat_duration)

        beats_since_change = self.beat_count - self.last_change
        if beats_since_change != 0 and beats_since_change % 32 == 0:
            self.next_visualization()

        # print(
        #     f"\r{60 / self.beat_duration:.2f} BPM ({self.beat_duration:.2f} s)",
        #     end="    ",
        # )
        progression = (now - self.last_beats[0]) / self.beat_duration
        viz = self.visualizations[self.visualization_index]
        self.last_frame = viz.apply(self.last_frame, delta, progression, self.beat)
        io.display.pixels = self.last_frame
        self.last = now

    def destroy(self):
        self.reset()
