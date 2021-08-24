"""Base classes for strategy games with opponents
"""
import time
from applications.games import core
from helpers import textutils, bitmaputils, animations
from applications.menu import SlidingChoice, Choice
from IO.color import *
import threading


class Move:
    """A move, which can be applied on a field to transform it to a new field
    """

    def apply(self, field):
        """Apply that move on a filed to transform it
        """
        raise NotImplementedError("Please implement this method")

    def __eq__(self, other):
        return repr(self) == repr(other)


class Field:
    """A representation of a playing field of a strategy game
    """

    def score(self, player):
        """Calculate a score for the given player on the field. Higher scores mean the player is more likely to win.
        """
        raise NotImplementedError("Please implement this method")

    def possible_moves(self, player):
        """Returns a list of moves that the given player could perform on the current state of the game
        """
        raise NotImplementedError("Please implement this method")

    def has_won(self, player):
        """Checks whether the given player has won the game
        """
        raise NotImplementedError("Please implement this method")

    def game_over(self):
        """Checks whether the game is finished
        """
        raise NotImplementedError("Please implement this method")

    def winning_moves(self):
        """Returns a list of moves that contribute to the winning player's victory
        """
        raise NotImplementedError("Please implement this method")


class BitField(Field):
    """2D field with two colors, implemented with bitboards for efficiency
    """
    UNDEFINED = 2
    EMPTY = 0
    COLOR1 = 1
    COLOR2 = -1

    # Constants used for bit count
    M1 = 0x5555555555555555
    M2 = 0x3333333333333333
    M4 = 0x0f0f0f0f0f0f0f0f
    H01 = 0x0101010101010101

    def __init__(self, width=8, height=8, bits1=0, bits2=0):
        self.height = height
        self.width = width
        self.bits1 = bits1
        self.bits2 = bits2

    @staticmethod
    def other(color):
        """Returns the opponent of the given color
        """
        return -color

    @staticmethod
    def count_bits(x):
        """Counts the bits that are set to 1 in a given integer
        """
        return bin(x).count("1")

    def get_bitmask(self, x, y):
        """Returns a bitmask which has only one bit set to 1, at the given location
        """
        return 1 << (x + y * self.width)

    def set_value(self, x, y, value):
        """Changes the field at the given position to the given value
        """
        mask = self.get_bitmask(x, y)
        if value == self.EMPTY:
            self.bits1 &= ~mask
            self.bits2 &= ~mask
        elif value == self.COLOR1:
            self.bits1 |= mask
            self.bits2 &= ~mask
        elif value == self.COLOR2:
            self.bits1 &= ~mask
            self.bits2 |= mask
        else:
            self.bits1 |= mask
            self.bits2 |= mask

    def get_value(self, x, y):
        """Returns the value of the field at the given position
        """
        mask = self.get_bitmask(x, y)
        if self.bits1 & mask == 0:
            if self.bits2 & mask == 0:
                return self.EMPTY
            else:
                return self.COLOR2
        else:
            if self.bits2 & mask == 0:
                return self.COLOR1
            else:
                return self.UNDEFINED

    def is_full(self):
        """Checks whether no position is empty
        """
        for x in range(self.width):
            for y in range(self.height):
                if self.get_value(x, y) == self.EMPTY:
                    return False
        return True

    def __str__(self):
        out = [
            f"{self.__class__.__name__} -  X: {self.score(self.COLOR1)} ({self.has_won(self.COLOR1)}) "
            f"O: {self.score(self.COLOR2)} ({self.has_won(self.COLOR2)})"]
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
        return f"\n{sep}\n".join(out)


class AlphaBeta:
    """An implementation of the alpha beta game tree algorithm
    """
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

        best_score = self.ALPHA_INIT - 1
        best_move = None
        for move in field.possible_moves(self.player):
            next_field = move.apply(field)
            score = self.get_min(
                next_field,
                AlphaBeta.ALPHA_INIT,
                AlphaBeta.BETA_INIT,
                self.depth - 1)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def get_max(self, field, alpha, beta, depth):
        """Returns the best score of any move if the current player wants to maximize the score
        """
        if self.time_over < time.time():
            raise TimeoutError()
        elif field.has_won(self.other):
            return -AlphaBeta.WIN_SCORE * (depth + 1)
        elif field.is_full() or depth <= 0:
            return field.score(self.player)

        best_score = self.ALPHA_INIT
        for move in field.possible_moves(self.player):
            next_field = move.apply(field)
            score = self.get_min(next_field, alpha, beta, depth - 1)
            if score > best_score:
                alpha = score
                best_score = score
            if alpha >= beta:
                return alpha
        return best_score

    def get_min(self, field, alpha, beta, depth):
        """Returns the best score of any move if the current player wants to minimize the score
        """
        if self.time_over < time.time():
            raise TimeoutError()
        elif field.has_won(self.player):
            return AlphaBeta.WIN_SCORE * (depth + 1)
        elif field.is_full() or depth <= 0:
            return field.score(self.player)

        best_score = self.BETA_INIT
        for move in field.possible_moves(self.other):
            next_field = move.apply(field)
            score = self.get_max(next_field, alpha, beta, depth - 1)
            if score < best_score:
                beta = score
                best_score = score
            if alpha >= beta:
                return beta
        return best_score


class Strategy:
    """A strategy, either of a human or a computer player, which can play a game
    """
    def __init__(self, color):
        self.color = color

    def make_move(self, io, delta, field, left, top):
        """Return a move on the given field
        """
        raise NotImplementedError("Please Implement this method")


class Applyer:
    """Sorry for this ugly thing, it was necessary to get around some list-comprehension issues I had
    """
    def __init__(self, game, strategy):
        self.game = game
        self.strategy = strategy

    def __call__(self, *args, **kwargs):
        self.game.set_player(self.strategy)


class TreadWithResult(threading.Thread):
    """A thread that can return the return value of the given function after its done
    """
    def __init__(
            self,
            *thread_args,
            target=None,
            args=(),
            kwargs=None,
            **thread_kwargs):
        if kwargs is None:
            kwargs = {}

        self.result = None

        def function():
            """Helper function that runs the target function and stores its return value for later usage"""
            self.result = target(*args, **kwargs)

        super().__init__(*thread_args, target=function, **thread_kwargs)


class AIPlayer(Strategy):
    """Strategy for a game that uses the alpha beta algorithm to determine its move
    """
    def __init__(self, time_limit, max_depth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_limit = time_limit
        self.max_depth = max_depth
        self.thread = None

    def _make_move(self, field):
        finish_time = time.time() + self.time_limit
        move = None
        for d in range(1, self.max_depth + 1):
            try:
                time_left = finish_time - time.time()
                move = AlphaBeta(d, time_left)(self.color, field)
            except TimeoutError as _:
                # print("AI ran out of time at depth", d)
                return move
        # print("AI finished analysis with depth", d, self.max_depth, move)
        return move

    def make_move(self, io, delta, field, left, top):
        """Return a move on the given field
        """
        if self.thread is None:
            self.thread = TreadWithResult(
                target=self._make_move, args=(field,))
            self.thread.start()
        elif not self.thread.is_alive():
            self.thread.join()
            out = self.thread.result
            self.thread = None
            return out
        else:
            return None


class HumanPlayer(Strategy):
    """Lets a human choose its moves on a strategy game
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.select_blinker = animations.Blinker(Color(128, 128, 128), WHITE)
        self.selected_move = None

    def make_move(self, io, delta, field, left, top):
        """Return a move on the given field
        """
        possible_moves = list(field.possible_moves(self.color))
        if len(possible_moves) == 0:
            return None

        if self.selected_move is None or self.selected_move not in possible_moves:
            self.selected_move = possible_moves[0]

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
            for p in possible_moves:
                delta_x = min(self.selected_move.x - p.x,
                              self.selected_move.x - p.x + field.width)
                delta_y = min(self.selected_move.y - p.y,
                              self.selected_move.y - p.y + field.height)

                score = 0
                if direction[0] == 0:
                    score += field.width - abs(delta_x)
                else:
                    sign = 1 if direction[0] * delta_x > 0 else -1
                    score += 100 * (field.width - abs(delta_x)) * sign

                if direction[1] == 0:
                    score += field.height - abs(delta_y)
                else:
                    sign = 1 if direction[1] * delta_y > 0 else -1
                    score += 100 * (field.height - abs(delta_y)) * sign

                if best_score is None or score > best_score:
                    best_score = score
                    best_field = p
            self.selected_move = best_field

        if self.selected_move is not None:
            io.display.update(
                left + self.selected_move.x,
                top + self.selected_move.y,
                self.select_blinker.tick(delta))

        if io.controller.a.get_fresh_value() == False:
            return self.selected_move
        else:
            return None


class StrategyGame(core.Game):
    """Base class for 2 Player Strategy games like TicTacToe and Connect4
    """
    FIELD_SIZE = (3, 3)
    FIELD_CLASS = BitField
    COLOR_MAP = {
        BitField.COLOR1: RED,
        BitField.COLOR2: BLUE,
    }

    DIFFICULTIES = {
        "Ea": (GREEN, 0.5, 2),
        "Me": (YELLOW, 1, 5),
        "Di": (RED, 5, 30)
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.player1 = None
        self.player2 = None

        self.player1Choice = SlidingChoice([
                                               Choice("Hu", WHITE, Applyer(self, HumanPlayer(BitField.COLOR1)))] + [
                                               Choice(name, color, Applyer(self, AIPlayer(t, d, BitField.COLOR1)))
                                               for name, (color, t, d) in self.DIFFICULTIES.items()], 8)

        self.player2Choice = SlidingChoice([
                                               Choice("Hu", WHITE, Applyer(self, HumanPlayer(BitField.COLOR2)))] + [
                                               Choice(name, color, Applyer(self, AIPlayer(t, d, BitField.COLOR2)))
                                               for name, (color, t, d) in self.DIFFICULTIES.items()], 8)
        self.reset()

    def reset(self, *args):
        """Resets the strategy game
        """
        super().reset(*args)
        self.player1 = None
        self.player2 = None
        self.field = None
        self.active_color = BitField.COLOR1
        self.border_ticker = animations.Ticker(0.1)
        self.select_blinker = animations.Blinker(Color(128, 128, 128), WHITE)
        self.p1_win_blinker = animations.Blinker(
            self.COLOR_MAP[BitField.COLOR1], WHITE, speed=1)
        self.p2_win_blinker = animations.Blinker(
            self.COLOR_MAP[BitField.COLOR2], WHITE, speed=1)
        self.gameover_scroller = None

        self.field_colors = [[animations.AnimatedColor((0, 0, 0), speed=2) for _ in range(
            self.FIELD_SIZE[1])] for _ in range(self.FIELD_SIZE[0])]

        self.border_color = animations.AnimatedColor(
            self.COLOR_MAP[BitField.COLOR1], speed=2)

    def set_player(self, player):
        """Helper function that stores the given player in slot 1 or 2, accoriding to the players color
        """
        if player.color == BitField.COLOR1:
            self.player1 = player
        else:
            self.player2 = player

    def player_select(self, io, delta, color):
        """Displays a player select screen
        """
        io.display.fill((0, 0, 0))
        idx = [BitField.COLOR1, BitField.COLOR2].index(color)

        bmp = textutils.get_text_bitmap(f"P{idx + 1}")
        bitmaputils.apply_bitmap(
            bmp, io.display, (1, 1), fg_color=self.COLOR_MAP[color])
        [self.player1Choice, self.player2Choice][idx].update(io, delta)

    def _update_pregame(self, io, delta):
        if self.player1 is None:
            self.player_select(io, delta, BitField.COLOR1)
        elif self.player2 is None:
            self.player_select(io, delta, BitField.COLOR2)
        else:
            self.field = self.FIELD_CLASS()
            self.state = self.MID_GAME

    def _update_midgame(self, io, delta):
        # Switch players if active player cannot move
        if len(list(self.field.possible_moves(self.active_color))) == 0:
            self.active_color = self.field.other(self.active_color)
            self.border_color.set_value(self.COLOR_MAP[self.active_color])
            if len(list(self.field.possible_moves(self.active_color))) == 0:
                self.state = self.GAME_OVER
                return

        left = int(5 - self.FIELD_SIZE[0] / 2)
        top = int(5 - self.FIELD_SIZE[1] / 2)
        self.draw_field(io, delta, left, top)

        if self.active_color == BitField.COLOR1:
            move = self.player1.make_move(io, delta, self.field, left, top)
        else:
            move = self.player2.make_move(io, delta, self.field, left, top)

        if move is not None:
            self.field = move.apply(self.field)
            if self.field.game_over():
                self.state = self.GAME_OVER
            else:
                self.active_color = self.field.other(self.active_color)
                self.border_color.set_value(self.COLOR_MAP[self.active_color])

    def _update_gameover(self, io, delta):
        if io.controller.a.get_fresh_value() == False:
            self.reset()
            self.state = self.PRE_GAME
            self.field = None
            self.player1 = None
            self.player2 = None
            self.gameover_scroller = None
        else:
            left = int(5 - self.FIELD_SIZE[0] / 2)
            top = int(5 - self.FIELD_SIZE[1] / 2)
            self.draw_field(io, delta, left, top)
            color1 = self.p1_win_blinker.tick(delta)
            color2 = self.p2_win_blinker.tick(delta)

            for move in self.field.winning_moves():
                if move.color == BitField.COLOR1:
                    io.display.update(left + move.x, top + move.y, color1)
                if move.color == BitField.COLOR2:
                    io.display.update(left + move.x, top + move.y, color2)

            if self.field.has_won(BitField.COLOR1):
                self.active_color = BitField.COLOR1
                text = "P1 WON!"
                color = self.COLOR_MAP[BitField.COLOR1]
            elif self.field.has_won(BitField.COLOR2):
                self.active_color = BitField.COLOR2
                text = "P2 WON!"
                color = self.COLOR_MAP[BitField.COLOR2]
            else:
                text = "DRAW!"
                color = WHITE

            text_bmp = textutils.get_text_bitmap(text)

            if self.gameover_scroller is None:
                self.gameover_scroller = animations.Ticker(
                    4 / (text_bmp.shape[1] + 10))
            self.gameover_scroller.tick(delta)

            x = int((1 - self.gameover_scroller.progression) *
                    (text_bmp.shape[1] + 10) - text_bmp.shape[1])
            y = top + \
                self.FIELD_SIZE[1] + 1 + max(0, ((15 - (top + self.FIELD_SIZE[1] + 1) - 5) // 2))
            bitmaputils.apply_bitmap(
                text_bmp, io.display, (x, y), fg_color=color)

    @staticmethod
    def get_background_color(x, y):
        """Gets the background color for the given position
        """
        if (x + y) % 2 == 0:
            return (0, 0, 0)
        else:
            return (32, 32, 32)

    def draw_border(self, io, delta, left, top):
        """Draws the border around the field
        """
        right = left + self.FIELD_SIZE[0]
        bottom = top + self.FIELD_SIZE[1]
        self.border_ticker.tick(delta)
        self.border_color.tick(delta)
        color = self.border_color.get_value()

        coordinates = [(x, top - 1) for x in range(left - 1, right + 1)] + \
                      [(right, y) for y in range(top, bottom + 1)] + \
                      [(x, bottom) for x in range(right, left - 1, -1)] + \
                      [(left - 1, y) for y in range(bottom, top - 1, -1)]

        for i, coord in enumerate(coordinates):
            prog = 1 - self.border_ticker.progression + i / len(coordinates)
            prog -= int(prog)
            if prog < 0.1:
                prog = (0.1 - prog) / 0.1

            io.display.update(
                *coord, tuple(map(lambda c: c * (0.5 + 0.5 * prog), color)))

    def draw_stones(self, io, delta, left, top):
        """Draws the stones on the field
        """
        for x in range(self.FIELD_SIZE[0]):
            for y in range(self.FIELD_SIZE[1]):
                c = self.field.get_value(x, y)
                if c in self.COLOR_MAP:
                    self.field_colors[x][y].set_value(self.COLOR_MAP[c])
                else:
                    self.field_colors[x][y].set_value(
                        self.get_background_color(x, y))
                self.field_colors[x][y].tick(delta)

        for x in range(self.FIELD_SIZE[0]):
            for y in range(self.FIELD_SIZE[1]):
                io.display.update(
                    left + x, top + y, self.field_colors[x][y].get_value())

    def draw_field(self, io, delta, left, top):
        """Draws both the border and the stones
        """
        io.display.fill((0, 0, 0))
        self.draw_border(io, delta, left, top)
        self.draw_stones(io, delta, left, top)

    def _update(self, io, delta):
        pass


if __name__ == "__main__":
    bf = BitField(6, 7)
    bf.set_value(4, 4, BitField.COLOR2)
    print(str(bf))
