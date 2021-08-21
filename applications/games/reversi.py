from applications.games import alphabeta
import random
import numpy as np


class ReversiMove(alphabeta.Move):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
    
    def __repr__(self):
        return f"Move({self.x}, {self.y}, {self.color})"

    def apply(self, field):
        clone = ReversiField(bits1=field.bits1, bits2=field.bits2)
        flips, count = clone.flipped_stones(self.x, self.y, self.color)
        
        if self.color == ReversiField.COLOR1:
            clone.bits1 |= flips
            clone.bits2 &= ~flips
            clone.count1 = field.count1 + count
            clone.count2 = field.count2 - count + 1
        else:
            clone.bits1 &= ~flips
            clone.bits2 |= flips
            clone.count1 = field.count1 - count + 1
            clone.count2 = field.count2 + count
        
        return clone

class ReversiField(alphabeta.BitField):
    def __init__(self, *args, count1=2, count2=2, bits1=0x18000000, bits2=0x1800000000, **kwargs):
        super().__init__(*args, width=8, height=8, bits1=bits1, bits2=bits2, **kwargs)
        self.possible = [None, None]
        self.count1 = count1
        self.count2 = count2
                    
    def set_value(self, *args, **kwargs):
        super().set_value(*args, **kwargs)
        self.possible = [None, None]

    @staticmethod
    def move_n(board):
        return board >> 8

    @staticmethod
    def move_ne(board):
        return (board >> 7) & 0xfefefefefefefefe

    @staticmethod
    def move_e(board):
        return (board << 1) & 0xfefefefefefefefe

    @staticmethod
    def move_se(board):
        return (board << 9) & 0xfefefefefefefe00

    @staticmethod
    def move_s(board):
        return (board << 8) & 0xffffffffffffff00

    @staticmethod
    def move_sw(board):
        return (board << 7) & 0x7f7f7f7f7f7f7f00

    @staticmethod
    def move_w(board):
        return (board >> 1) & 0x7f7f7f7f7f7f7f7f

    @staticmethod
    def move_nw(board):
        return (board >> 9) & 0x7f7f7f7f7f7f7f7f

    def score(self, player):
        out = self._playerscore(player) - self._playerscore(self.other(player))
        return out

    def _playerscore(self, player):
        if player == self.COLOR1:
            bits = self.bits1
            count = self.count1
        else:
            bits = self.bits2
            count = self.count2

        return 1000 * self.count_bits(bits & 0x8100000000000081) + \
                238 * len(self.possible_moves(player)) + \
                -166 * self.count_bits(bits & 0x4281000000008142) + \
                -401 * self.count_bits(bits & 0x42000000004200) + \
                -26 * count


    @staticmethod
    def possible_dir(player, opponent, possible, move_function):
        # There has to be at least one opponent
        player = move_function(player)
        opponent = move_function(opponent)
        possible &= opponent

        final = 0
        while possible != 0:
            player = move_function(player)
            opponent = move_function(opponent)

            # Add stones followed by player to possible list
            new_final = player & possible
            possible &= ~new_final
            final |= new_final

            # Otherwise if opponent follows keep
            possible &= opponent

        return final

    def possible_moves(self, player):
        if player == self.COLOR1:
            index = 0
        else:
            index = 1
        if self.possible[index] is None:
            if player == self.COLOR1:
                player_bits = self.bits1
                opponent_bits = self.bits2
            else:
                player_bits = self.bits2
                opponent_bits = self.bits1

            free = ~player_bits & ~opponent_bits

            possible_bitmap = self.possible_dir(player_bits, opponent_bits, free, self.move_n) | \
                        self.possible_dir(player_bits, opponent_bits, free, self.move_ne) | \
                        self.possible_dir(player_bits, opponent_bits, free, self.move_e) | \
                        self.possible_dir(player_bits, opponent_bits, free, self.move_se) | \
                        self.possible_dir(player_bits, opponent_bits, free, self.move_s) | \
                        self.possible_dir(player_bits, opponent_bits, free, self.move_sw) | \
                        self.possible_dir(player_bits, opponent_bits, free, self.move_w) | \
                        self.possible_dir(player_bits, opponent_bits, free, self.move_nw)

            self.possible[index] = [ReversiMove(x, y, player) for x in range(self.width) for y in range(self.height) if possible_bitmap & self.get_bitmask(x, y) != 0]
        return self.possible[index]

    def flipped_stones(self, x, y, player):
        other = self.other(player)

        flips = self.get_bitmask(x, y)
        count = 1
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            x2 = x+dx
            y2 = y+dy
            if not (0 <= x2 < self.width and 0 <= y2 < self.height) or self.get_value(x2, y2) != other:
                continue

            flips_dir = self.get_bitmask(x2, y2)
            count_dir = 1
            x2 += dx
            y2 += dy
            while 0 <= x2 < self.width and 0 <= y2 < self.height and self.get_value(x2, y2) == other:
                flips_dir |= self.get_bitmask(x2, y2)
                count_dir += 1
                x2 += dx
                y2 += dy

            if 0 <= x2 < self.width and 0 <= y2 < self.height and self.get_value(x2, y2) == player:
                count += count_dir
                flips |= flips_dir
        return flips, count

    def has_won(self, player):
        if not self.game_over():
            return False
        elif player == self.COLOR1:
            return self.count1 > self.count2
        else:
            return self.count2 > self.count1
        
    def is_full(self):
        return self.bits1 | self.bits2 == 0xffffffffffffffff

    def game_over(self):
        return self.is_full() or (len(self.possible_moves(self.COLOR1)) == 0 and len(self.possible_moves(self.COLOR2)) == 0)

    def winning_moves(self):
        if self.has_won(self.COLOR1):
            color = self.COLOR1
            bits = self.bits1
        elif self.has_won(self.COLOR2):
            color = self.COLOR2
            bits = self.bits2
        else:
            return []
        return [ReversiMove(x, y, color) for x in range(self.width) for y in range(self.height) if bits & self.get_bitmask(x, y) != 0]

class Reversi(alphabeta.StrategyGame):
    FIELD_SIZE = (8, 8)
    FIELD_CLASS = ReversiField
