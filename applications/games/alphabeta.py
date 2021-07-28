import time
from applications.games import core
from helpers import textutils, bitmaputils
from applications.menu import SlidingChoice, Choice
import threading

class Move:
    def apply(self, field):
        raise NotImplementedError("Please implement this method")

    def __eq__(self, other):
        return repr(self) == repr(other)

class Field:
    def score(self, player):
        raise NotImplementedError("Please implement this method")

    def possible_moves(self, player):
        raise NotImplementedError("Please implement this method")

    def has_won(self, player):
        raise NotImplementedError("Please implement this method")

    def game_over(self):
        raise NotImplementedError("Please implement this method")

    def winning_moves(self):
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

class Strategy:
    def __init__(self, color):
        self.color = color

    def make_move(self, io, delta, field):
        raise NotImplementedError("Please Implement this method")
    

# Sorry for this ugly thing...
class Applyer:
    def __init__(self, game, strategy):
        self.game = game
        self.strategy = strategy
    
    def __call__(self, *args, **kwargs):
        self.game.set_player(self.strategy)

class TreadWithResult(threading.Thread):
    def __init__(self, *threadArgs, target=None, args=(), kwargs={}, **threadKwargs):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(*threadArgs, target=function, **threadKwargs)

class AIPlayer(Strategy):
    def __init__(self, time_limit, max_depth, *args, **kwargs):
        print(time_limit, max_depth)
        super().__init__(*args, **kwargs)
        self.time_limit = time_limit
        self.max_depth = max_depth
        self.thread = None
        move = None

    def _make_move(self, field):
        finish_time = time.time() + self.time_limit
        move = None
        for d in range(1, self.max_depth+1):
            try:
                time_left = finish_time - time.time()
                move = AlphaBeta(d, time_left)(self.color, field)
            except Exception as e:
                print("AI ran out of time at depth", d)
                print(e)
                return move
        print("AI finished analysis with depth", d, self.max_depth)
        return move

    def make_move(self, io, delta, field, left, top):
        if self.thread is None:
            self.thread = TreadWithResult(target=self._make_move, args=(field,))
            self.thread.start()
        elif not self.thread.is_alive():
            self.thread.join()
            out = self.thread.result
            self.thread = None
            return out
        else:
            return None

class HumanPlayer(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.select_blinker = core.Blinker((128, 128, 128), (256, 256, 256))
        self.selected_move = None

    def make_move(self, io, delta, field, left, top):
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
                    score += 100 * \
                        (field.width - abs(delta_x)) * sign

                if direction[1] == 0:
                    score += field.height - abs(delta_y)
                else:
                    sign = 1 if direction[1] * delta_y > 0 else -1
                    score += 100 * \
                        (field.height - abs(delta_y)) * sign

                if best_score is None or score > best_score:
                    best_score = score
                    best_field = p
            self.selected_move = best_field

        if self.selected_move is not None:
            io.display.update(left + self.selected_move.x, top + self.selected_move.y,
                                self.select_blinker.tick(delta))

        if io.controller.a.get_fresh_value():
            return self.selected_move
        else:
            return None


class StrategyGame(core.Game):
    FIELD_SIZE = (3, 3)
    FIELD_CLASS = BitField
    COLOR_MAP = {
        BitField.COLOR1: (255, 0, 0),
        BitField.COLOR2: (0, 255, 0),
    }
    DIFFICULTIES = {
        "Ea": ((0, 255, 0), 1, 2),
        "Me": ((255, 255, 0), 2, 10),
        "Di": ((255, 0, 0), 5, 30)
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player1 = None
        
        self.player1Choice = SlidingChoice([
            Choice("Hu", (255, 255, 255), Applyer(self, HumanPlayer(BitField.COLOR1)))
            ] + [Choice(name, color, Applyer(self, AIPlayer(t, d, BitField.COLOR1))) for name, (color, t, d) in self.DIFFICULTIES.items()]
            , 8)

        self.player2 = None
        self.player2Choice = SlidingChoice([
            Choice("Hu", (255, 255, 255), Applyer(self, HumanPlayer(BitField.COLOR2)))
            ] + [Choice(name, color, Applyer(self, AIPlayer(t, d, BitField.COLOR2))) for name, (color, t, d) in self.DIFFICULTIES.items()]
            , 8)
        
        self.field = None
        self.active_color = BitField.COLOR1
        self.border_ticker = core.Ticker(0.1)
        self.select_blinker = core.Blinker((128, 128, 128), (256, 256, 256))
        self.p1_win_blinker = core.Blinker(self.COLOR_MAP[BitField.COLOR1], (256, 256, 256), speed=2)
        self.p2_win_blinker = core.Blinker(self.COLOR_MAP[BitField.COLOR2], (256, 256, 256), speed=2)
        self.gameover_scroller = None

    def set_player(self, player):
        if player.color == BitField.COLOR1:
            self.player1 = player
        else:
            self.player2 = player
        
    def player_select(self, io, delta, color):
        io.display.fill((0,0,0))
        idx = [BitField.COLOR1, BitField.COLOR2].index(color)

        bmp = textutils.getTextBitmap(f"P{idx+1}")
        bitmaputils.applyBitmap(bmp, io.display, (1, 1), fg_color=self.COLOR_MAP[color])
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
        left = int(5 - self.FIELD_SIZE[0]/2)
        top = int(5 - self.FIELD_SIZE[1]/2)
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

    def _update_gameover(self, io, delta):
        if io.controller.a.get_fresh_value():
            self.state = self.PRE_GAME
            self.field = None
            self.player1 = None
            self.player2 = None
            self.gameover_scroller = None
        else:
            left = int(5 - self.FIELD_SIZE[0]/2)
            top = int(5 - self.FIELD_SIZE[1]/2)
            self.draw_field(io, delta, left, top)
            color1 = self.p1_win_blinker.tick(delta)
            color2 = self.p2_win_blinker.tick(delta)
            
            for move in self.field.winning_moves():
                if move.color == BitField.COLOR1:
                    io.display.update(left + move.x, top + move.y, color1)
                if move.color == BitField.COLOR2:
                    io.display.update(left + move.x, top + move.y, color2)
            
            if self.field.has_won(BitField.COLOR1):
                text = "P1 WON!"
                color = self.COLOR_MAP[BitField.COLOR1]
            elif self.field.has_won(BitField.COLOR2):
                text = "P2 WON!"
                color = self.COLOR_MAP[BitField.COLOR2]
            else:
                text = "DRAW!"
                color = (255, 255, 255)

            text_bmp = textutils.getTextBitmap(text)

            if self.gameover_scroller is None:
                self.gameover_scroller = core.Ticker(4/(text_bmp.shape[1]+10))
            self.gameover_scroller.tick(delta)

            x = int((1-self.gameover_scroller.progression) * (text_bmp.shape[1] + 10) - text_bmp.shape[1])
            y = top + self.FIELD_SIZE[1] + 1 + max(0, ((15 - (top + self.FIELD_SIZE[1] + 1) - 5)//2))
            bitmaputils.applyBitmap(text_bmp, io.display, (x, y), fg_color=color)

    def get_background_color(self, x, y):
        if (x + y) % 2 == 0:
            return (64, 64, 64)
        else:
            return (32, 32, 32)

    def draw_border(self, io, delta, left, top):
        right = left + self.FIELD_SIZE[0]
        bottom = top + self.FIELD_SIZE[1]
        self.border_ticker.tick(delta)

        coordinates = [(x, top-1) for x in range(left-1, right+1)] + \
            [(right, y) for y in range(top, bottom+1)] + \
            [(x, bottom) for x in range(right, left-1, -1)] + \
            [(left-1, y) for y in range(bottom, top-1, -1)]

        for i, coord in enumerate(coordinates):
            prog = 1-self.border_ticker.progression + i/len(coordinates)
            prog = 4 * (prog - int(prog) - 0.5)**2

            io.display.update(*coord, tuple(map(lambda c:c*(0.5 + 0.5*prog), self.COLOR_MAP[self.active_color])))

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

    def draw_field(self, io, delta, left, top):
        io.display.fill((0, 0, 0))
        self.draw_border(io, delta, left, top)
        self.draw_stones(io.display, left, top)

    def _update(self, io, delta):
        pass


if __name__ == "__main__":
    bf = BitField(6, 7)
    bf.set_value(4, 4, BitField.COLOR2)
    print(str(bf))
