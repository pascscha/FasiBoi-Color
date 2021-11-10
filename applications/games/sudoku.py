from applications.games import puzzle
from helpers import animations
import numpy as np
from IO.color import *

levels = [
            [
                [1,6,0,9,8,5,0,0,0],
                [2,0,4,0,0,0,0,0,8],
                [3,5,7,4,0,0,3,6,0],
                [4,0,0,7,0,1,6,0,4],
                [5,0,0,0,5,4,9,0,2],
                [6,0,0,3,6,9,0,1,0],
                [7,0,9,5,4,0,1,0,0],
                [8,2,0,1,0,0,0,0,7],
                [9,0,0,2,0,0,0,0,3]
            ],
            [
                [0,6,0,9,8,5,0,0,0],
                [0,0,4,0,0,0,0,0,8],
                [8,5,7,4,0,0,3,6,0],
                [0,0,0,7,0,1,6,0,4],
                [1,0,0,0,5,4,9,0,2],
                [4,0,0,3,6,9,0,1,0],
                [7,0,9,5,4,0,1,0,0],
                [0,2,0,1,0,0,0,0,7],
                [6,0,0,2,0,0,0,0,3]
            ],
            [
                [0,0,0,0,9,0,0,0,0],
                [0,3,2,0,0,7,0,0,0],
                [0,0,0,0,0,5,0,3,0],
                [0,0,0,0,6,0,9,0,7],
                [6,0,0,0,0,4,3,0,0],
                [0,0,0,7,2,0,0,0,4],
                [0,0,0,0,0,0,4,0,3],
                [1,0,0,8,0,0,0,0,0],
                [4,6,0,0,0,2,0,5,0]
            ]
        ]

class Sudoku(puzzle.Puzzle):
    def reset(self, io):
        self.levels = levels
        self.guesses = np.zeros((9,9), dtype=np.uint8)
        self.known = np.array(self.levels[self.current_level], dtype=np.uint8)
        self.selected = [0, 0]
        self.colors = [[animations.AnimatedColor(Color(0, 0, 0), speed=2) for _ in range(9)] for _ in range(9)]

        differences = np.array([0.05, 0.07, 0.1, 0.3, 0.1, 0.15, 0.07, 0.1, 0.1])
        differences /= sum(differences)

        hues = [sum(differences[:i]) for i in range(9)]

        self.color_map = [Color(0,0,0)] + [Color.from_hsv(hue, 1, 1) for hue in hues]

        self.draw_blinker = animations.Blinker(BLACK, WHITE)
        self.hint_blinker = animations.Blinker(WHITE, BLACK)

    @staticmethod
    def get_background_color(x, y):
        if (x//3 + y//3) % 2 == 0:
            return WHITE * 0.2
        else:
            return Color(0, 0, 0)

    def _update_midgame(self, io, delta):
        io.display.fill(BLACK)

        if io.controller.button_left.fresh_press():
            self.selected[0] -= 1
        if io.controller.button_right.fresh_press():
            self.selected[0] += 1
        if io.controller.button_up.fresh_press():
            self.selected[1] -= 1
        if io.controller.button_down.fresh_press():
            self.selected[1] += 1
        self.selected[0] = min(8, max(0, self.selected[0]))
        self.selected[1] = min(8, max(0, self.selected[1]))

        if io.controller.button_a.fresh_release():
            if self.known[self.selected[0]][self.selected[1]] == 0:
                self.guesses[self.selected[0]][self.selected[1]] += 1
                self.guesses[self.selected[0]][self.selected[1]] %= 10

        if io.controller.button_b.fresh_release():
            self.guesses[self.selected[0]][self.selected[1]] = 0

        hint_idx = None   
        if self.known[self.selected[0]][self.selected[1]] != 0:
            hint_idx = self.known[self.selected[0]][self.selected[1]]
        elif self.guesses[self.selected[0]][self.selected[1]] != 0:
            hint_idx = self.guesses[self.selected[0]][self.selected[1]]

        for x in range(9):
            for y in range(9):
                if self.known[x][y] == hint_idx:
                    self.colors[x][y].set_value(self.color_map[self.known[x][y]])
                elif self.guesses[x][y] == hint_idx:
                    self.colors[x][y].set_value(self.color_map[self.guesses[x][y]])
                elif self.known[x][y] != 0:
                    self.colors[x][y].set_value(self.color_map[self.known[x][y]] * 0.5)
                elif self.guesses[x][y] != 0:
                    self.colors[x][y].set_value(self.color_map[self.guesses[x][y]] * 0.5)
                else:
                    self.colors[x][y].set_value(self.get_background_color(x, y))   

                field_color = self.colors[x][y].tick(delta)

                if x == self.selected[0] and y == self.selected[1]:
                    self.draw_blinker.value1 = field_color
                    io.display.update(x+1, y+3, self.draw_blinker.tick(delta))
                else:
                    io.display.update(x+1, y+3, field_color)

        for x in range(9):
            if x//3 % 2 == 0:
                io.display.update(x+1, 2, WHITE*0.5)
                io.display.update(x+1, 12, WHITE*0.5)
            else:
                io.display.update(x+1, 2, WHITE*0.3)
                io.display.update(x+1, 12, WHITE*0.3)

        for y in range(9):
            if y//3 % 2 == 0:
                io.display.update(0, y+3, WHITE*0.5)
            else:
                io.display.update(0, y+3, WHITE*0.3)
