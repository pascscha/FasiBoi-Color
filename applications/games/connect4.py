from applications.games import alphabeta
import random
import numpy as np


class Connect4Move(alphabeta.Move):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def __repr__(self):
        return f"Move({self.x}, {self.y}, {self.color})"

    def apply(self, field):
        clone = Connect4Field(bits1=field.bits1, bits2=field.bits2)
        clone.set_value(self.x, self.y, self.color)
        return clone


class Connect4Field(alphabeta.BitField):
    # All directions 4 in a row could appear
    DIRECTIONS = [
        (0, 1),  # Vertical |
        (1, 0),  # Horizontal -
        (1, 1),  # Diagonal /
        (-1, 1),  # Diagonal \
    ]

    # Masks for each row (vertical)
    ROW_MASKS = np.array([0x0000000000003f,
                          0x00000000003f00,
                          0x000000003f0000,
                          0x0000003f000000,
                          0x00003f00000000,
                          0x003f0000000000,
                          0x3f000000000000], dtype=np.int64)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, width=8, height=8, **kwargs)

    def score(self, player):
        return self.count3(player) - self.count3(self.other(player))

    def possible_moves(self, player):
        out = []
        for x in [3, 2, 4, 5, 1, 0, 6]:
            for y in range(self.height - 3, -1, -1):
                if self.get_value(x, y) == 0:
                    out.append(Connect4Move(x, y, player))
                    break
        return out

    def has_won(self, player):
        if player == self.COLOR1:
            board = self.bits1
        else:
            board = self.bits2

        # Diagonal \
        y = board & board >> 7
        if y & (y >> 14):
            return True

        # Horizontal -
        y = board & board >> 8
        if y & (y >> 16):
            return True

        # Diagonal /
        y = board & board >> 9
        if y & (y >> 18):
            return True

        # Vertical |
        y = board & board >> 1
        if y & (y >> 2):
            return True

        return False

    def count3(self, player):
        if player == self.COLOR1:
            board = self.bits1
            other = self.bits2
        else:
            board = self.bits2
            other = self.bits1

        # vertical
        possible = (board << 1) & (board << 2) & (board << 3)  # straight up

        # horizontal
        intermed = (board << 8) & (board << 16)  # two on left
        possible |= intermed & (board << 24)  # XXX.
        possible |= intermed & (board >> 8)  # XX.X

        intermed = (board >> 8) & (board >> 16)  # two on right
        possible |= intermed & (board >> 24)  # .XXX
        possible |= intermed & (board << 8)  # X.XX

        # diagonal 1
        intermed = (board << 7) & (board << 16)
        possible |= intermed & (board << 21)
        possible |= intermed & (board >> 7)
        intermed = (board >> 7) & (board >> 16)
        possible |= intermed & (board >> 21)
        possible |= intermed & (board << 7)

        # diagonal 2
        intermed = (board << 9) & (board << 18)
        possible |= intermed & (board << 27)
        possible |= intermed & (board >> 9)
        intermed = (board >> 9) & (board >> 18)
        possible |= intermed & (board >> 27)
        possible |= intermed & (board << 9)

        possible &= ~other

        # Weighted
        return 7 * self.count_bits(possible & 0x01010101010101) + \
            6 * self.count_bits(possible & 0x02020202020202) +\
            5 * self.count_bits(possible & 0x04040404040404) +\
            4 * self.count_bits(possible & 0x08080808080808) +\
            3 * self.count_bits(possible & 0x10101010101010) +\
            2 * self.count_bits(possible & 0x20202020202020) +\
            1 * self.count_bits(possible & 0x40404040404040)

    def is_full(self):
        return (self.bits1 | self.bits2) & 0x7f == 0x7f

    def game_over(self):
        return self.is_full() or self.has_won(self.COLOR1) or self.has_won(self.COLOR2)

    def rows(self, player):
        if player == self.COLOR1:
            board = self.bits1
        else:
            board = self.bits2

        out = 0

        # Diagonal \
        y = board & board >> 7
        y2 = y & (y >> 14)
        y3 = y2 | y2 << 14
        out |= y3 | y3 << 7

        # Horizontal -
        y = board & board >> 8
        y2 = y & (y >> 16)
        y3 = y2 | y2 << 16
        out |= y3 | y3 << 8

        # Diagonal /
        y = board & board >> 9
        y2 = y & (y >> 18)
        y3 = y2 | y2 << 9
        out |= y3 | y3 << 18

        # Vertical |
        y = board & board >> 1
        y2 = y & (y >> 2)
        y3 = y2 | y2 << 2
        out |= y3 | y3 << 1

        for x in range(7):
            for y in range(self.height - 3, -1, -1):
                if self.get_bitmask(x, y) & out:
                    yield Connect4Move(x, y, player)

    def winning_moves(self):
        return list(self.rows(self.COLOR1)) + list(self.rows(self.COLOR2))


class Connect4(alphabeta.StrategyGame):
    FIELD_SIZE = (7, 6)
    FIELD_CLASS = Connect4Field
