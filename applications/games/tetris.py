from applications.games import core
import random
import numpy as np
import time


class Tetromino():
    def __init__(self, rot, color=0):
        self.color = color
        self.rotations = []
        self.rotations += rot
        self.nrot = len(self.rotations)

    def get_color(self):
        return self.color

    def get_nrot(self):
        return self.nrot

    def get_rotation(self, i):
        return np.copy(self.rotations[i][1]), np.copy(self.rotations[i][0])


class TetrominoList():
    I = [(np.array([0, 1, 2, 3]), np.array([1, 1, 1, 1])),
         (np.array([0, 0, 0, 0]), np.array([0, 1, 2, 3]))]
    O = [(np.array([0, 0, 1, 1]), np.array([1, 2, 1, 2]))]
    L = [(np.array([0, 1, 2, 2]), np.array([1, 1, 1, 2])),
         (np.array([1, 1, 1, 0]), np.array([0, 1, 2, 2])),
         (np.array([0, 0, 1, 2]), np.array([1, 2, 2, 2])),
         (np.array([0, 0, 0, 1]), np.array([0, 1, 2, 0]))]
    J = [(np.array([0, 1, 2, 2]), np.array([2, 2, 2, 1])),
         (np.array([0, 0, 0, 1]), np.array([0, 1, 2, 2])),
         (np.array([0, 0, 1, 2]), np.array([1, 2, 1, 1])),
         (np.array([1, 1, 1, 0]), np.array([0, 1, 2, 0]))]
    T = [(np.array([0, 0, 0, 1]), np.array([0, 1, 2, 1])),
         (np.array([0, 1, 1, 2]), np.array([1, 1, 2, 1])),
         (np.array([1, 1, 1, 0]), np.array([0, 1, 2, 1])),
         (np.array([0, 1, 1, 2]), np.array([2, 2, 1, 2]))]
    Z = [(np.array([0, 0, 1, 1]), np.array([0, 1, 1, 2])),
         (np.array([0, 1, 1, 2]), np.array([2, 1, 2, 1]))]
    S = [(np.array([0, 0, 1, 1]), np.array([2, 1, 1, 0])),
         (np.array([0, 1, 1, 2]), np.array([1, 2, 1, 2]))]

    COLOR_I = (0, 255, 255)
    COLOR_O = (255, 255, 0)
    COLOR_L = (255, 127, 0)
    COLOR_J = (0, 0, 255)
    COLOR_T = (128, 0, 128)
    COLOR_Z = (255, 0, 0)
    COLOR_S = (0, 255, 0)
    COLOR_B = (0, 0, 0)
    COLOR_G = (128, 128, 128)

    COLORS = [COLOR_I, COLOR_O, COLOR_L, COLOR_J,
              COLOR_T, COLOR_Z, COLOR_S, COLOR_B]

    def __init__(self):
        self.tetlist = []
        for tet, (idx, color) in zip([self.I, self.O, self.L, self.J, self.T, self.Z, self.S], enumerate(self.COLORS)):
            self.tetlist.append(Tetromino(tet, idx))

    def sample(self):
        return random.choice(self.tetlist)


class Tetris(core.Game):
    # Directions
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    BG = 7

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tl = TetrominoList()

    def reset(self, io):
        self.gb = np.ones((10, 18))*self.BG
        self.gb_shape = (10, 15)
        self.score = 0
        self.game_over_counter = 0

        self.tetromino = self.tl.sample()
        self.curr_rot = 0
        self.curr_pos_x, self.curr_pos_y = self.tetromino.get_rotation(0)
        self.curr_shift_y = 3-max(self.curr_pos_y)
        self.curr_shift_x = 3
        self.curr_pos_x += self.curr_shift_x

        # Set speed and progression of Tetrominos. Progression accumulates the time that has passed since last movement.
        self.ticker = core.Ticker(3)

    def _update_midgame(self, io, delta):

        self.gb[self.curr_pos_x, self.curr_pos_y] = self.BG

        # Check controller values. We look for fresh_values, because we only care
        # about button presses and not if the button is held down
        if io.controller.left.get_value():
            d = self.LEFT[0]
            if self.check(self.curr_pos_x+d, self.curr_pos_y, io):
                self.curr_pos_x += d
                self.curr_shift_x += d
        if io.controller.right.get_value():
            d = self.RIGHT[0]
            if self.check(self.curr_pos_x+d, self.curr_pos_y, io):
                self.curr_pos_x += d
                self.curr_shift_x += d
        if io.controller.down.get_value():
            d = self.DOWN[1]
            if self.check(self.curr_pos_x, self.curr_pos_y+d, io):
                self.curr_pos_y += d
                self.curr_shift_y += d
        if io.controller.a.get_fresh_value():
            self.curr_rot = (self.curr_rot - 1) % self.tetromino.nrot
            new_pos_x, new_pos_y = self.tetromino.get_rotation(self.curr_rot)
            new_pos_x += self.curr_shift_x-int(np.median(new_pos_x))
            new_pos_y += self.curr_shift_y-int(np.median(new_pos_y))
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
            if self.check(self.curr_pos_x, self.curr_pos_y+d, io):
                self.curr_pos_y += d
                self.curr_shift_y += d
                self.gb[self.curr_pos_x,
                        self.curr_pos_y] = self.tetromino.get_color()
            else:
                self.gb[self.curr_pos_x,
                        self.curr_pos_y] = self.tetromino.get_color()
                self.check_gb(io)
                self.new_tetromino(io)
        else:
            self.gb[self.curr_pos_x,
                    self.curr_pos_y] = self.tetromino.get_color()

        # Draw Gameboard
        for x, y in np.ndindex(self.gb_shape):
            io.display.update(x, y, self.tl.COLORS[int(self.gb[x, y+3])])

    def _update_gameover(self, io, delta):
        self.ticker.speed = 6
        if self.game_over_counter >= 18:
            self.state = self.PRE_GAME
        if self.ticker.tick(delta):
            for x, y in np.ndindex(self.gb_shape):
                col = self.tl.COLOR_B
                if self.gb[x, y+3] != self.BG:
                    col = self.tl.COLOR_G
                io.display.update(x, y, col)
            self.shift_rows(self.game_over_counter)
            self.game_over_counter += 1

    def check(self, new_x, new_y, io):
        for x, y in zip(new_x, new_y):
            if x >= io.display.width or x < 0:
                return False
            if y >= io.display.height+3 or y < 0:
                return False
            if self.gb[x, y] != self.BG:
                return False
        return True

    def new_tetromino(self, io):
        self.ticker.speed += 0.01
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
            self.shift_rows(idx, io)
        self.score += 2**len(to_delete)-1

    def shift_rows(self, idx, io=None):
        if io is not None:
            brightness = 255
            pulse= False
            for count in range(5):
                # Draw pulsating line
                pulse= not pulse
                for x in range(10):
                    io.display.update(x, idx-3, (brightness*pulse,
                                                brightness*pulse, brightness*pulse))
                io.display.refresh()
                time.sleep(0.1)
            
        top = np.ones([10]) * self.BG
        for i in range(idx, 0, -1):
            self.gb[:, i] = self.gb[:, i-1]
        self.gb[:, 0] = top
