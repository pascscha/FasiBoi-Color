from applications.games import core
from helpers import animations
import random
import numpy as np
import time
from IO.color import *


class Tetromino:
    def __init__(self, rot, color=0, name=""):
        self.color = color
        self.rotations = []
        self.rotations += rot
        self.nrot = len(self.rotations)
        self.name = name

    def get_color(self):
        return self.color

    def get_nrot(self):
        return self.nrot

    def get_rotation(self, i):
        return np.copy(self.rotations[i][1]), np.copy(self.rotations[i][0])
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

class TetrominoList:
    SHAPE_I = [
        (np.array([0, 1, 2, 3]), np.array([1, 1, 1, 1])),
        (np.array([0, 0, 0, 0]), np.array([0, 1, 2, 3])),
    ]
    SHAPE_O = [(np.array([0, 0, 1, 1]), np.array([1, 2, 1, 2]))]
    SHAPE_L = [
        (np.array([0, 1, 2, 2]), np.array([1, 1, 1, 2])),
        (np.array([1, 1, 1, 0]), np.array([0, 1, 2, 2])),
        (np.array([0, 0, 1, 2]), np.array([1, 2, 2, 2])),
        (np.array([0, 0, 0, 1]), np.array([0, 1, 2, 0])),
    ]
    SHAPE_J = [
        (np.array([0, 1, 2, 2]), np.array([2, 2, 2, 1])),
        (np.array([0, 0, 0, 1]), np.array([0, 1, 2, 2])),
        (np.array([0, 0, 1, 2]), np.array([1, 2, 1, 1])),
        (np.array([1, 1, 1, 0]), np.array([0, 1, 2, 0])),
    ]
    SHAPE_T = [
        (np.array([0, 0, 0, 1]), np.array([0, 1, 2, 1])),
        (np.array([0, 1, 1, 2]), np.array([1, 1, 2, 1])),
        (np.array([1, 1, 1, 0]), np.array([0, 1, 2, 1])),
        (np.array([0, 1, 1, 2]), np.array([2, 2, 1, 2])),
    ]
    SHAPE_Z = [
        (np.array([0, 0, 1, 1]), np.array([0, 1, 1, 2])),
        (np.array([0, 1, 1, 2]), np.array([2, 1, 2, 1])),
    ]
    SHAPE_S = [
        (np.array([0, 0, 1, 1]), np.array([2, 1, 1, 0])),
        (np.array([0, 1, 1, 2]), np.array([1, 2, 1, 2])),
    ]

    COLOR_I = (0, 255, 255)
    COLOR_O = (255, 255, 0)
    COLOR_L = (255, 127, 0)
    COLOR_J = (0, 0, 255)
    COLOR_T = (128, 0, 128)
    COLOR_Z = (255, 0, 0)
    COLOR_S = (0, 255, 0)
    COLOR_B = (0, 0, 0)
    COLOR_G = (128, 128, 128)

    COLORS = [COLOR_I, COLOR_O, COLOR_L, COLOR_J, COLOR_T, COLOR_Z, COLOR_S, COLOR_B]

    SAMPLE_REPETITIONS = 4

    def __init__(self):
        self.tetlist = []
        self.sample_list = []

        for tet, (idx, color), name in zip(
            [
                self.SHAPE_I,
                self.SHAPE_O,
                self.SHAPE_L,
                self.SHAPE_J,
                self.SHAPE_T,
                self.SHAPE_Z,
                self.SHAPE_S,
            ],
            enumerate(self.COLORS),
            [
                'I','O','L','J','T','Z', 'S'
            ]
        ):
            self.tetlist.append(Tetromino(tet, idx, name=name))

    def fill_tetlist(self):
        for i in range(self.SAMPLE_REPETITIONS):
            self.sample_list += self.tetlist
        random.shuffle(self.sample_list)

    def sample(self):
        if len(self.sample_list) == 0:
            self.fill_tetlist()

        # print(list(reversed(self.sample_list)))

        out = self.sample_list[0]
        self.sample_list = self.sample_list[1:]
        return out


class Tetris(core.Game):
    # Directions
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    BG = 7
    ACCELERATION = 0.05

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tl = TetrominoList()

    def reset(self, io):
        self.gb = np.ones((10, 18)) * self.BG
        self.gb_shape = (10, 15)
        self.score = 0
        self.game_over_counter = 0

        self.tl.fill_tetlist()
        self.tetromino = self.tl.sample()
        self.curr_rot = 0
        self.curr_pos_x, self.curr_pos_y = self.tetromino.get_rotation(0)
        self.curr_shift_y = 3 - max(self.curr_pos_y)
        self.curr_shift_x = 3
        self.curr_pos_x += self.curr_shift_x

        # Set speed and progression of Tetrominos. Progression accumulates the
        # time that has passed since last movement.
        self.ticker = animations.Ticker(3)
        self.move_ticker = animations.Ticker(12)

        self.line_blinker = animations.Blinker(Color(128, 128, 128), WHITE, speed=5)
        self.blink_time = 0.5
        self.blink_start = None
        self.blink_rows = []


    def _update_midgame(self, io, delta):
        if (
            self.blink_start is not None
            and time.time() - self.blink_start < self.blink_time
        ):
            color = self.line_blinker.tick(delta)
            for idx in self.blink_rows:
                for x in range(io.display.width):
                    io.display.update(x, idx - 3, color)
        else:
            for idx in self.blink_rows:
                self.shift_rows(idx)
            self.blink_rows = []

            self.blink_start = None
            self.gb[self.curr_pos_x, self.curr_pos_y] = self.BG

            # Check controller values.
            pressed_l = False
            pressed_r = False
            pressed_d = False

            if io.controller.button_left.get_value():
                d = self.LEFT[0]
                if self.check(self.curr_pos_x + d, self.curr_pos_y, io) or pressed_l:
                    if self.move_ticker.tick(delta):
                        self.curr_pos_x += d
                        self.curr_shift_x += d
            if io.controller.button_right.get_value():
                d = self.RIGHT[0]
                if self.check(self.curr_pos_x + d, self.curr_pos_y, io) or pressed_r:
                    if self.move_ticker.tick(delta):
                        self.curr_pos_x += d
                        self.curr_shift_x += d
            if io.controller.button_down.get_value():
                d = self.DOWN[1]
                if self.check(self.curr_pos_x, self.curr_pos_y + d, io) or pressed_d:
                    if self.move_ticker.tick(delta):
                        self.curr_pos_y += d
                        self.curr_shift_y += d
            if io.controller.button_a.fresh_release() or io.controller.button_up.fresh_release():
                self.curr_rot = (self.curr_rot - 1) % self.tetromino.nrot
                new_pos_x, new_pos_y = self.tetromino.get_rotation(self.curr_rot)
                new_pos_x += self.curr_shift_x - int(np.median(new_pos_x))
                new_pos_y += self.curr_shift_y - int(np.median(new_pos_y))
                shift_x = 0
                while min(new_pos_x) < 0:
                    new_pos_x += 1
                    shift_x += 1
                while max(new_pos_x) >= io.display.width:
                    new_pos_x -= 1
                    shift_x -= 1
                if self.check(new_pos_x, new_pos_y, io):
                    self.curr_pos_y = new_pos_y
                    self.curr_pos_x = new_pos_x
                    self.curr_shift_x += shift_x
                else:
                    self.curr_rot = (self.curr_rot + 1) % self.tetromino.nrot

            # Move the Tetromino down if the time is ready
            if self.ticker.tick(delta):
                d = self.DOWN[1]
                if self.check(self.curr_pos_x, self.curr_pos_y + d, io):
                    self.curr_pos_y += d
                    self.curr_shift_y += d
                    self.gb[
                        self.curr_pos_x, self.curr_pos_y
                    ] = self.tetromino.get_color()
                else:
                    self.gb[
                        self.curr_pos_x, self.curr_pos_y
                    ] = self.tetromino.get_color()
                    self.check_gb(io)
                    self.new_tetromino(io)
            else:
                self.gb[self.curr_pos_x, self.curr_pos_y] = self.tetromino.get_color()

            # Draw Gameboard
            for x, y in np.ndindex(self.gb_shape):
                io.display.update(x, y, self.tl.COLORS[int(self.gb[x, y + 3])])

    def _update_gameover(self, io, delta):
        self.ticker.speed = 6
        if self.game_over_counter >= 18:
            self.state = self.PRE_GAME
        if self.ticker.tick(delta):
            for x, y in np.ndindex(self.gb_shape):
                col = self.tl.COLOR_B
                if self.gb[x, y + 3] != self.BG:
                    col = self.tl.COLOR_G
                io.display.update(x, y, col)
            self.shift_rows(self.game_over_counter)
            self.game_over_counter += 1

    def check(self, new_x, new_y, io):
        for x, y in zip(new_x, new_y):
            if x >= io.display.width or x < 0:
                return False
            if y >= io.display.height + 3 or y < 0:
                return False
            if self.gb[x, y] != self.BG:
                return False
        return True

    def new_tetromino(self, io):
        self.ticker.speed += self.ACCELERATION
        self.tetromino = self.tl.sample()
        self.curr_rot = 0
        self.curr_pos_x, self.curr_pos_y = self.tetromino.get_rotation(0)
        self.curr_shift_y = 0
        self.curr_shift_x = 3
        self.curr_pos_x += self.curr_shift_x
        if not self.check(self.curr_pos_x, self.curr_pos_y, io):
            self.state = self.GAME_OVER

    def check_gb(self, io):
        to_delete = np.where(np.any(self.gb == self.BG, axis=0) == False)
        to_delete = list(to_delete[0])
        for idx in to_delete:
            self.blink_rows.append(idx)
            self.blink_start = time.time()
        self.score += 2 ** len(to_delete) - 1

    def shift_rows(self, idx, io=None):
        if io is not None:
            brightness = 255
            pulse = False
            for count in range(5):
                # Draw pulsating line
                pulse = not pulse
                for x in range(10):
                    io.display.update(
                        x,
                        idx - 3,
                        (brightness * pulse, brightness * pulse, brightness * pulse),
                    )
                io.display.refresh()
                time.sleep(0.1)

        top = np.ones([10]) * self.BG
        for i in range(idx, 0, -1):
            if i < self.gb.shape[1]:
                self.gb[:, i] = self.gb[:, i - 1]
        self.gb[:, 0] = top
