from applications.games import core
from applications.games.alphabeta import BitField
from helpers import animations
from IO.color import *
import random
import itertools

import matplotlib.pyplot as plt


class MineUtils():

    @classmethod
    def get_neighbours(cls, x, y, width, height):

        xs = [x-1, x, x+1]
        rows = [x for x in xs if x >= 0 and x < width]
        ys = [y-1, y, y+1]
        cols = [x for x in ys if x >= 0 and x < height]

        neighbours = list(itertools.product(rows, cols))
        return neighbours

    @classmethod
    def generate_mines(cls, width, height, n_mines):
        possible_mines = list(itertools.product(range(width), range(height)))
        random.shuffle(possible_mines)
        mines = possible_mines[:n_mines]

        mine_field = BitField(width, height)
        for mine in mines:
            mine_field.set_value(mine[0], mine[1], BitField.COLOR1)

        numbers = np.zeros((width, height))
        for x, row in enumerate(numbers):
            for y, elem in enumerate(row):
                if mine_field.get_value(x, y) == BitField.COLOR1:
                    numbers[x, y] = -1
                    continue
                for (nx, ny) in MineUtils.get_neighbours(x, y, width, height):
                    if mine_field.get_value(nx, ny) == BitField.COLOR1:
                        numbers[x, y] += 1
        return mine_field, numbers


class MineSweeper(core.Game):
    FIXSIZES = False
    SIZE_X = 10
    SIZE_Y = 15
    N_MINES = 17
    DEFAULT_SCORE = 9999999
    MISERE = True

    NOT_VISITED = 100
    NOTHING = 0
    FLAG = -10
    MINE = -1

    ONE = BLUE
    TWO = GREEN
    THREE = RED
    FOUR = Color(0, 0, 128)
    FIVE = Color(128, 0, 0)
    SIX = Color(0, 128, 0)

    number_colors = {
        FLAG: Color(255, 255, 0),
        MINE: Color(255, 255, 0),
        NOTHING: Color(170, 170, 170),
        1: ONE,
        2: TWO,
        3: THREE,
        4: FOUR,
        5: FIVE,
        6: SIX
    }

    def reveal(self):
        if self.numbers[self.pos] == 0:
            self.visited = []
            self.recursive_reveal(self.pos)
        self.visible[self.pos] = self.numbers[self.pos]

    def recursive_reveal(self, pos):
        if self.numbers[pos] == 0 and pos not in self.visited:
            self.visited.append(pos)
            neighbours = MineUtils.get_neighbours(
                *pos, self.SIZE_X, self.SIZE_Y)
            for n in neighbours:
                self.recursive_reveal(n)
        self.visible[pos] = self.numbers[pos]

    def check_won(self):
        flags = self.visible == self.FLAG
        if np.sum(flags) == self.N_MINES:
            self.state = self.GAME_OVER
            self.visible = self.numbers
            print(self.score)

    def reset(self, io):
        if not self.FIXSIZES:
            self.SIZE_X = io.display.width
            self.SIZE_Y = io.display.height

        self.visible = np.ones((self.SIZE_X, self.SIZE_Y))*self.NOT_VISITED
        self.pos = (self.SIZE_X // 2, self.SIZE_Y // 2)
        self.pos_blinker = animations.Blinker(
            Color(255, 218, 0), Color(126, 95, 0), speed=2)
        self.score = 0

    def _update_midgame(self, io, delta):
        new_pos = self.pos
        self.score += delta

        if io.controller.button_a.fresh_press():
            
            if np.sum(np.abs(self.visible)) == self.NOT_VISITED*self.SIZE_X*self.SIZE_Y:
                print("new")
                empty = False
                while not empty:
                    self.mine_field, self.numbers = MineUtils.generate_mines(
                        self.SIZE_X, self.SIZE_Y, self.N_MINES)
                    if self.numbers[self.pos] == 0:
                        empty = True
                self.reveal()
            
            if self.mine_field.get_value(*self.pos) == BitField.COLOR1:
                self.score = 9999999999
                self.state = self.GAME_OVER
                print(self.score)
            
            else:
                self.reveal()

        if io.controller.button_b.fresh_press():
            if np.sum(np.abs(self.visible)) == self.NOT_VISITED*self.SIZE_X*self.SIZE_Y:
                print("new")
            else:
                self.visible[self.pos] = self.FLAG
                self.check_won()

        if io.controller.button_left.fresh_press():
            new_pos = (self.pos[0]-1, self.pos[1])
        if io.controller.button_right.fresh_press():
            new_pos = (self.pos[0]+1, self.pos[1])
        if io.controller.button_up.fresh_press():
            new_pos = (self.pos[0], self.pos[1]-1)
        if io.controller.button_down.fresh_press():
            new_pos = (self.pos[0], self.pos[1]+1)

        if 0 <= new_pos[0] < self.SIZE_X and 0 <= new_pos[1] < self.SIZE_Y:
            self.pos = new_pos

        io.display.fill((0, 0, 0))
        for x in range(io.display.width):
            for y in range(io.display.height):
                if self.visible[x, y] != self.NOT_VISITED:
                    io.display.update(
                        x, y, self.number_colors[self.visible[x, y]])

        io.display.update(*self.pos, self.pos_blinker.tick(delta))
        plt.show()

    def _update_gameover(self, io, delta):
        if io.controller.button_a.fresh_release():
            self.state = self.PRE_GAME

if __name__ == "__main__":
    MineSweeper.generate_maze(10, 15)
