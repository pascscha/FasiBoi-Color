import time
from applications.games import core
from helpers import textutils, bitmaputils

class Move:
    def apply(self, field):
        raise NotImplementedError("Please implement this method")


class Field:
    def score(self, player):
        raise NotImplementedError("Please implement this method")

    def possible_moves(self, player):
        raise NotImplementedError("Please implement this method")

    def has_won(self, player):
        raise NotImplementedError("Please implement this method")

    def game_over(self):
        raise NotImplementedError("Please implement this method")


class BitField(Field):
    EMPTY = 0
    COLOR1 = 1
    COLOR2 = -1

    def __init__(self, width=8, height=8, bits1=0, bits2=0):
        self.height = height
        self.width = width
        self.bits1 = bits1
        self.bits2 = bits2

    @staticmethod
    def other(color):
        return -color

    def get_bitmask(self, x, y):
        return 1 << (x + y*self.width)

    def set_value(self, x, y, value):
        mask = self.get_bitmask(x, y)
        if value == self.EMPTY:
            self.bits1 &= ~mask
            self.bits2 &= ~mask
        if value == self.COLOR1:
            self.bits1 |= mask
            self.bits2 &= ~mask
        if value == self.COLOR2:
            self.bits1 &= ~mask
            self.bits2 |= mask

    def get_value(self, x, y):
        mask = self.get_bitmask(x, y)
        if self.bits1 & mask:
            return self.COLOR1
        elif self.bits2 & mask:
            return self.COLOR2
        else:
            return self.EMPTY

    def is_full(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.get_value(x, y) == self.EMPTY:
                    return False
        return True

    def __str__(self):
        out = [
            f"{self.__class__.__name__} -  X: {self.score(self.COLOR1)} ({self.has_won(self.COLOR1)}) O: {self.score(self.COLOR2)} ({self.has_won(self.COLOR2)})"]
        for y in range(self.height):
            line = []
            for x in range(self.width):
                color = self.get_value(x, y)
                if color == self.COLOR1:
                    line.append("X")
                elif color == self.COLOR2:
                    line.append("O")
                else:
                    line.append(" ")
            out.append(" | ".join(line))
        sep = "-" * len(out[-1])
        return (f"\n{sep}\n").join(out)


class AlphaBeta:
    ALPHA_INIT = -111111111111
    BETA_INIT = -ALPHA_INIT
    WIN_SCORE = 100000

    def __init__(self, depth, timeout):
        self.depth = depth
        self.timeout = timeout

    def __call__(self, player, field):
        self.player = player
        self.other = field.other(self.player)
        self.time_over = time.time() + self.timeout

        bestScore = self.ALPHA_INIT
        bestMove = None
        for move in field.possible_moves(self.player):
            next_field = move.apply(field)
            score = self.get_min(
                next_field, AlphaBeta.ALPHA_INIT, AlphaBeta.BETA_INIT, self.depth-1)
            if score > bestScore:
                bestScore = score
                bestMove = move
        return bestMove

    def get_max(self, field, alpha, beta, depth):
        if self.time_over < time.time():
            raise TimeoutError()
        elif field.has_won(self.other):
            return -AlphaBeta.WIN_SCORE * (depth+1)
        elif field.is_full() or depth <= 0:
            return field.score(self.player)

        bestScore = self.ALPHA_INIT
        for move in field.possible_moves(self.player):
            next_field = move.apply(field)
            score = self.get_min(next_field, alpha, beta, depth-1)
            if score > bestScore:
                alpha = score
                bestScore = score
            if alpha >= beta:
                return alpha
        return bestScore

    def get_min(self, field, alpha, beta, depth):
        if self.time_over < time.time():
            raise TimeoutError()
        elif field.has_won(self.player):
            return AlphaBeta.WIN_SCORE * (depth+1)
        elif field.is_full() or depth <= 0:
            return field.score(self.player)

        bestScore = self.BETA_INIT
        for move in field.possible_moves(self.other):
            next_field = move.apply(field)
            score = self.get_max(next_field, alpha, beta, depth-1)
            if score < bestScore:
                beta = score
                bestScore = score
            if alpha >= beta:
                return beta
        return bestScore


class StrategyGame(core.Game):
    FIELD_SIZE = (3, 3)
    FIELD_CLASS = BitField
    COLOR_MAP = {
        BitField.COLOR1: (255, 0, 0),
        BitField.COLOR2: (0, 255, 255),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player1 = None
        self.player2 = None
        self.active_color = BitField.COLOR1
        self.select_blinker = core.Blinker((128, 128, 128), (256, 256, 256))

    def player_select(self, io, delta, color):
        bmp = textutils.getTextBitmap(f"P{[BitField.COLOR1, BitField.COLOR2].index(color)+1}")
        io.display.fill((0,0,0))
        bitmaputils.applyBitmap(bmp, io.display, (2, 0), fg_color=self.COLOR_MAP[color])

    def _update_midgame(self, io, delta):
        if self.player1 is None:
            self.player_select(io, delta, BitField.COLOR1)
        else:
            self.draw_field(io, delta)

    def get_background_color(self, x, y):
        if (x + y) % 2 == 0:
            return (64, 64, 64)
        else:
            return (32, 32, 32)

    def draw_border(self, display, left, top):
        right = left + self.FIELD_SIZE[0]
        bottom = top + self.FIELD_SIZE[1]

        coordinates = [(x, top-1) for x in range(left-1, right+1)] + \
            [(right, y) for y in range(top, bottom+1)] + \
            [(x, bottom) for x in range(right, left-1, -1)] + \
            [(left-1, y) for y in range(bottom, top-1, -1)]

        for i, coord in enumerate(coordinates):
            display.update(*coord, tuple(map(lambda c:c//2, self.COLOR_MAP[self.active_color])))

    def draw_stones(self, display, left, top):
        for x in range(self.FIELD_SIZE[0]):
            for y in range(self.FIELD_SIZE[1]):
                c = self.field.get_value(x, y)
                if c in self.COLOR_MAP:
                        display.update(left + x, top + y,
                                   self.COLOR_MAP[c])
                else:
                    display.update(left + x, top + y,
                                   self.get_background_color(x, y))

    def draw_highlight(self, io, delta, left, top):
        if self.possible_fields is not None and len(self.possible_fields) > 0:
            if self.selected_field is None or self.selected_field not in self.possible_fields:
                self.selected_field = self.possible_fields[0]

            direction = None
            if io.controller.left.get_fresh_value():
                direction = (1, 0)
            if io.controller.right.get_fresh_value():
                direction = (-1, 0)
            if io.controller.up.get_fresh_value():
                direction = (0, 1)
            if io.controller.down.get_fresh_value():
                direction = (0, -1)

            if direction is not None:
                best_score = None
                best_field = None
                for p in self.possible_fields:
                    delta_x = min(self.selected_field.x - p.x,
                                  self.selected_field.x - p.x + self.FIELD_SIZE[0])
                    delta_y = min(self.selected_field.y - p.y,
                                  self.selected_field.y - p.y + self.FIELD_SIZE[1])

                    score = 0
                    if direction[0] == 0:
                        score += self.FIELD_SIZE[0] - abs(delta_x)
                    else:
                        sign = 1 if direction[0] * delta_x > 0 else -1
                        score += 100 * \
                            (self.FIELD_SIZE[0] - abs(delta_x)) * sign

                    if direction[1] == 0:
                        score += self.FIELD_SIZE[1] - abs(delta_y)
                    else:
                        sign = 1 if direction[1] * delta_y > 0 else -1
                        score += 100 * \
                            (self.FIELD_SIZE[1] - abs(delta_y)) * sign

                    if best_score is None or score > best_score:
                        best_score = score
                        best_field = p
                self.selected_field = best_field

            if self.selected_field is not None:
                io.display.update(left + self.selected_field.x, top + self.selected_field.y,
                                  self.select_blinker.tick(delta))

    def draw_field(self, io, delta):
        left = int(5 - self.FIELD_SIZE[0]/2)
        top = int(5 - self.FIELD_SIZE[1]/2)

        io.display.fill((0, 0, 0))
        self.draw_border(io.display, left, top)
        self.draw_stones(io.display, left, top)
        self.draw_highlight(io, delta, left, top)

        if io.controller.a.get_fresh_value():
            if self.selected_field is not None:
                self.field = self.selected_field.apply(self.field)
                self.active_color = self.field.other(self.active_color)
                self.possible_fields = list(self.field.possible_moves(
                    self.active_color))
                if self.field.has_won(self.active_color) or self.field.has_won(self.field.other(self.active_color)):
                    self.state = self.GAME_OVER

    def _update(self, io, delta):
        pass


if __name__ == "__main__":
    bf = BitField(6, 7)
    bf.set_value(4, 4, BitField.COLOR2)
    print(str(bf))
