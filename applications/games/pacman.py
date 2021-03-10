from applications.games import core
import random
import numpy as np


class Pacman(core.Game):
    WALL = 1
    FOOD = 2
    SUPER_FOOD = 3
    GHOST_DOOR = 4

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def fresh_field(self):
        return np.load("resources/sprites/pacman.npy")

    def reset(self, io):
        self.field = self.fresh_field()
        self.pacman = (4, 11)
        self.pacman_direction = self.RIGHT
        self.button_press_queue = []

        self.packman_ticker = core.Ticker(5)

    def is_walkable(self, x, y):
        width, height = self.field.shape
        x %= width
        y %= height
        return self.field[x][y] not in [self.WALL, self.GHOST_DOOR]
        
    def _update_midgame(self, io, delta):
        if io.controller.left.get_fresh_value():
            self.button_press_queue.append(self.LEFT)
        if io.controller.right.get_fresh_value():
            self.button_press_queue.append(self.RIGHT)
        if io.controller.up.get_fresh_value():
            self.button_press_queue.append(self.UP)
        if io.controller.down.get_fresh_value():
            self.button_press_queue.append(self.DOWN)

        if self.packman_ticker.tick(delta):
            valid = False
            while not valid and len(self.button_press_queue) > 0:
                direction = self.button_press_queue[0]
                self.button_press_queue = self.button_press_queue[1:]
                if self.is_walkable(self.pacman[0] + direction[0], self.pacman[1] + direction[1]):
                    valid = True
                    self.pacman_direction = direction

            x = self.pacman[0] + self.pacman_direction[0]
            y = self.pacman[1] + self.pacman_direction[1]
            x %= self.field.shape[0]
            y %= self.field.shape[1]            
            if self.is_walkable(x,y):
                self.pacman = (x,y)
                self.field[x][y] = 0
        io.display.fill((0, 0, 0))

        prog1 = self.pulse_progression*2
        prog2 = self.pulse_progression
        bright1 = int(255 * (abs(prog1 - int(prog1) - 0.5)*0.5+0.5))
        bright2 = int(128 * (abs(prog2 - int(prog2) - 0.5)*0.25+0.75))

        for x in range(io.display.width):
            for y in range(io.display.height):
                val = self.field[x][y]
                if val == self.WALL:
                    io.display.update(x, y, (0, 0, 255))
                elif val == self.FOOD:
                    io.display.update(x, y, (bright2, bright2, bright2))
                elif val == self.SUPER_FOOD:
                    io.display.update(x, y, (bright1, bright1, bright1))

        io.display.update(*self.pacman, (255, 255, 0))
