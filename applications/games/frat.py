from applications.games import core
from helpers import animations, textutils, bitmaputils
import random
import time

class Frat(core.Game):
    MISERE = True
    DEFAULT_SCORE = 99

    COLOR_MAP = {
        1: (255, 0, 0),
        2: (0, 255, 0),
        3: (0, 0, 255),
        4: (255, 255, 0)
    }
    
    MODE_GUESS = 0
    MODE_DRAW = 1
    COLOR_GUESS = (0, 255, 255)
    COLOR_DRAW = (255, 0, 255)
    SUBMIT_TIME = 3

    def reset(self, io):
        self.mode = self.MODE_GUESS
        self.border_color = animations.AnimatedColor(self.COLOR_GUESS, speed=2)
        self.border_ticker = core.Ticker(0.1)
        self.both_down_ts = 0

        self.selected = [0, 0]
        self.guess_blinker = [core.Blinker((32, 32, 32), (255, 255, 255)) for i in range(4)]
        self.draw_blinker = core.Blinker((32, 32, 32), (255, 255, 255))

        self.score = 0
        self.field = [[0 for _ in range(8)] for _ in range(8)]
        self.counts = {0:64, 1:0, 2:0, 3:0, 4:0}

        self.guessed = [[False for _ in range(7)] for _ in range(7)]

        self.hint_colors = [animations.AnimatedColor((64, 64, 64), speed=4) for _ in range(4)]        

        # TODO: Auto Generate
        self.solution = [[1, 1, 1, 1, 1, 4, 4, 2],
                         [1, 3, 1, 4, 4, 4, 2, 2],
                         [1, 3, 1, 1, 1, 4, 4, 2],
                         [1, 3, 3, 4, 4, 4, 2, 2],
                         [1, 3, 4, 4, 4, 2, 2, 2],
                         [1, 3, 3, 2, 4, 4, 4, 2],
                         [1, 1, 3, 2, 2, 2, 2, 2],
                         [3, 3, 3, 3, 3, 3, 3, 3]]

        self.gameover_blinker = [[core.Blinker((0, 0, 0), (0, 0, 0)) for _ in range(8)] for _ in range(8)]



    def draw_border(self, io, delta):
        if self.state == self.MID_GAME:
            if self.mode == self.MODE_GUESS:
                self.border_color.set_value(self.COLOR_GUESS)
            else:
                self.border_color.set_value(self.COLOR_DRAW)
            
        self.border_ticker.tick(delta)
        self.border_color.tick(delta)
        color = self.border_color.get_value()

        coordinates = [(x, 0) for x in range(0, 9)] + \
            [(9, y) for y in range(0, 9)] + \
            [(x, 9) for x in range(9, -1, -1)] + \
            [(0, y) for y in range(9, -1, -1)]

        for i, coord in enumerate(coordinates):
            prog = 1-self.border_ticker.progression + i/len(coordinates)
            prog = prog - int(prog)
            if prog < 0.1:
                prog = (0.1-prog)/0.1

            io.display.update(*coord, tuple(map(lambda c:c*(0.5 + 0.5*prog), color)))

    def get_background_color(self, x, y):
        if (x + y) % 2 == 0:
            return (0, 0, 0)
        else:
            return (32, 32, 32)

    def is_finished(self):
        for row in self.field:
            for c in row:
                if c == 0:
                    return False
        return True

    def _update_midgame(self, io, delta):        
        if io.controller.b.get_fresh_value() == False:
            if self.mode == self.MODE_GUESS:
                self.mode = self.MODE_DRAW
            else:
                self.mode = self.MODE_GUESS
        
        if io.controller.left.get_fresh_value():
            self.selected[0] -= 1
        if io.controller.right.get_fresh_value():
            self.selected[0] += 1
        if io.controller.up.get_fresh_value():
            self.selected[1] -= 1
        if io.controller.down.get_fresh_value():
            self.selected[1] += 1
        
        if self.mode == self.MODE_GUESS:
            limit = 6
        else:
            limit = 7        
        self.selected[0] = max(0, min(limit, self.selected[0]))
        self.selected[1] = max(0, min(limit, self.selected[1]))

        if io.controller.a.get_fresh_value() == False:
            if self.mode == self.MODE_GUESS:
                if not self.guessed[self.selected[0]][self.selected[1]]:
                    self.score += 1
                    self.guessed[self.selected[0]][self.selected[1]] = True
            else:
                self.counts[self.field[self.selected[0]][self.selected[1]]] -= 1
                self.field[self.selected[0]][self.selected[1]] = (self.field[self.selected[0]][self.selected[1]] + 1) % 5
                self.counts[self.field[self.selected[0]][self.selected[1]]] += 1
                
        if io.controller.a.get_value() and io.controller.b.get_value():
            if time.time() - self.both_down_ts > self.SUBMIT_TIME and self.is_finished():
                self.border_color.set_value((0, 255, 0))
                for x in range(8):
                    for y in range(8):
                        self.gameover_blinker[x][y].color1 = self.COLOR_MAP[self.field[x][y]]
                        self.gameover_blinker[x][y].color2 = self.COLOR_MAP[self.solution[x][y]]
                        if self.field[x][y] != self.solution[x][y]:
                            self.score = self.DEFAULT_SCORE
                            self.border_color.set_value((255, 0, 0))
                self.state = self.GAME_OVER
                return
        else:
            self.both_down_ts = time.time()



        io.display.fill((0, 0, 0))
        self.draw_border(io, delta)
        highlight_size = 1 if self.mode == self.MODE_DRAW else 2

        for x in range(8):
            for y in range(8):                    
                dx = x - self.selected[0]
                dy = y - self.selected[1]
                
                if 0 <= dx <= highlight_size-1 and 0 <= dy <= highlight_size-1:
                    if self.mode == self.MODE_DRAW:
                        blinker = self.draw_blinker
                    else:
                        blinker = self.guess_blinker[dx + 2*dy]

                    if self.field[x][y] == 0:
                        blinker.color2 = (255, 255, 255)
                    else:
                        blinker.color2 = self.COLOR_MAP[self.field[x][y]]
                    color = blinker.tick(delta)
                else:
                    if self.field[x][y] == 0:
                        color = self.get_background_color(x, y)
                    else:
                        color = self.COLOR_MAP[self.field[x][y]]
                
                io.display.update(1+x, 1+y, color)

        # self.guess_bmp = textutils.getTextBitmap(str(self.guesses))
        # bitmaputils.applyBitmap(self.guess_bmp, io.display, (3, 9))

        if self.mode == self.MODE_GUESS:
            if self.guessed[self.selected[0]][self.selected[1]]:
                values = [
                    self.solution[self.selected[0]][self.selected[1]],
                    self.solution[self.selected[0]+1][self.selected[1]],
                    self.solution[self.selected[0]][self.selected[1]+1],
                    self.solution[self.selected[0]+1][self.selected[1]+1]
                ]
                colors = [self.COLOR_MAP[c] for c in sorted(values)]
            else:
                colors = [(64, 64, 64)] * 4
        else:
            colors = [(0, 0, 0)] * 4

        for i, (h, c) in enumerate(zip(self.hint_colors, colors)):
            h.set_value(c)
            h.tick(delta)
            io.display.update(3 + i, 12, h.get_value())
        
        for color in range(1, 5):
            count = self.counts[color]
            mask = 1
            for bit in range(5):
                if mask & count:
                    if color < 3:
                        x = color - 1
                    else:
                        x = color + 5
                    io.display.update(x, 10 + bit, self.COLOR_MAP[color])
                mask = mask << 1

    def _update_gameover(self, io, delta):
        io.display.fill((0, 0, 0))
        self.draw_border(io, delta)

        for x in range(8):
            for y in range(8):
                io.display.update(x + 1, y + 1, self.gameover_blinker[x][y].tick(delta))

        if io.controller.a.get_fresh_value():
            self.state = self.PRE_GAME