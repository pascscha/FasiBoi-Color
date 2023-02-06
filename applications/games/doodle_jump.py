from applications.games import core
import random
import math


class DoodleJump(core.Game):

    bars = [(i, i + 1) for i in range(9)]

    def last(self, l, n):
        sum = 0
        for i in range(n):
            sum += len(l[i])
        return sum

    def get_random_line(self, n):
        if n <= 0:
            if self.last(self.green, 3) + self.last(self.blue, 3) == 0:
                n = 1
            else:
                return []
        p = []
        for i in range(n):
            poss = self.get_possible_bars(p)
            if len(poss) > 0:
                (b1, b2) = random.choice(poss)
                p.append((b1, b2))
        return p

    def get_possible_bars(self, p):
        possible = []
        for b1, b2 in self.bars:
            poss = True
            for bar in self.green[0]:
                if b1 in bar or b2 in bar:
                    poss = False
            for bar in p:
                if b1 in bar or b2 in bar:
                    poss = False
                elif b1 - 1 == bar[1] or b2 + 1 == bar[0]:
                    poss = False
            if poss:
                possible.append((b1, b2))

        return possible

    def reset(self, io):
        self.probmin = -5
        self.probmax = 3
        self.probblue = 5
        self.blue = [[] for i in range(io.display.height)]
        self.green = [[], [(3, 4)], []]
        for i in range(io.display.height - 3):
            n = random.randint(round(self.probmin), round(self.probmax))
            self.green = [self.get_random_line(n)] + self.green

        self.blue_ticker = core.Ticker(3)
        self.move_ticker = core.Ticker(12)

        self.gravity = 20
        self.gravity_progression = 0
        self.y_velocity = -2
        self.y_pos = 12.1
        self.x_pos = 4
        self.bg_pos = 0

        self.score = 0

    def _update_midgame(self, io, delta):

        if round(self.y_pos) <= 8 and self.y_velocity <= 0:
            self.bg_pos -= self.y_velocity * delta

            if self.bg_pos > 1:
                self.y_pos += self.bg_pos
                self.bg_pos = 0
                self.green.pop()
                self.blue.pop()
                n = random.randint(round(self.probmin), round(self.probmax))
                if n % self.probblue == 0:
                    self.blue = [self.get_random_line(n)] + self.blue
                    self.green = [[]] + self.green
                else:
                    self.green = [self.get_random_line(n)] + self.green
                    self.blue = [[]] + self.blue
                self.score += 1
                self.probmax -= 0.1
                self.probmin -= 0.1

        self.y_pos += self.y_velocity * delta

        # Check controller values.
        if self.on_bar(io) and self.y_velocity > 0:
            # self.y_pos -=0.1
            self.y_velocity = -12
            # self.y_velocity = min(-2, self.y_velocity)

        if io.controller.left.get_value():
            d = -1
            if self.move_ticker.tick(delta):
                self.x_pos += d

        if io.controller.right.get_value():
            d = 1
            if self.move_ticker.tick(delta):
                self.x_pos += d

        if self.x_pos < 0:
            self.x_pos = io.display.width - 1
        elif self.x_pos >= io.display.width:
            self.x_pos = 0

        if self.y_pos > io.display.height:
            self.y_velocity = 10
            self.y_pos = 0
            self.x_pos = 4
            self.state = self.GAME_OVER
            return

        self.y_velocity += self.gravity * delta

        io.display.fill((0, 0, 0))

        for y, bar in enumerate(self.green):
            if len(bar) > 0:
                for (x1, x2) in bar:
                    io.display.update(x1, y, (0, 255, 0))
                    io.display.update(x2, y, (0, 255, 0))

        display_location = round(self.y_pos)
        if 0 <= display_location < io.display.height:
            io.display.update(self.x_pos, round(self.y_pos), (255, 255, 0))

    def _update_gameover(self, io, delta):
        self.y_velocity += self.gravity * delta
        self.y_pos += self.y_velocity * delta
        io.display.fill((0, 0, 0))
        display_location = round(self.y_pos)
        if 0 <= display_location < io.display.height:
            io.display.update(self.x_pos, round(self.y_pos), (255, 255, 0))

        if self.y_pos > io.display.height:
            self.state = self.PRE_GAME

    def on_bar(self, io):
        if self.y_pos < 0:
            return False
        if round(self.y_pos) >= io.display.height - 1:
            return False
        check = self.green[round(self.y_pos + 1)]
        for bar in check:
            if self.x_pos in bar:
                return True
        return False
