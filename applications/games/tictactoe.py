from applications.games import alphabeta
from IO.color import *
import random

class TicTacToeMove(alphabeta.Move):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
    
    def __repr__(self):
        return f"Move({self.x}, {self.y}, {self.color})"

    def apply(self, field):
        clone = TicTacToeField(bits1=field.bits1, bits2=field.bits2)
        clone.set_value(self.x, self.y, self.color)
        return clone

class TicTacToeField(alphabeta.BitField):
    ROWS = [
        [(0,0),(0,1),(0,2)],
        [(1,0),(1,1),(1,2)],
        [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)],
        [(0,1),(1,1),(2,1)],
        [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)],
        [(0,2),(1,1),(2,0)]
    ]

    ORDER = [
        [(1,1)],
        [(0,0),(2,2),(0,2),(2,0)],
        [(0,1),(1,0),(1,2),(2,1)]
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, width=3, height=3, **kwargs)

    def score(self, player):
        score = 0
        other = self.other(player)
        for row in self.ROWS:
            rowscore = 0
            for x,y in row:
                col = self.get_value(x,y)
                if col == player:
                    rowscore += 1
                elif col == other:
                    rowscore -= 1
            if rowscore == 3:
                score += 32
            elif rowscore == -3:
                score -= 32
            elif abs(rowscore) == 2:
                score += rowscore
        return score

    def possible_moves(self, player):
        for x,y in self.ORDER[0] + self.ORDER[1] + self.ORDER[2]:
            if self.get_value(x, y) == self.EMPTY:
                yield TicTacToeMove(x, y, player)

    def has_won(self, player):
        for row in self.ROWS:
            if all(self.get_value(x, y) == player for x, y in row):
                return True
        return False
    
    def game_over(self):
        return self.is_full() or self.has_won(self.COLOR1) or self.has_won(self.COLOR2)

    def winning_moves(self):
        out = []
        for player in [self.COLOR1, self.COLOR2]:
            for row in self.ROWS:
                if all(self.get_value(x, y) == player for x, y in row):
                    out += [TicTacToeMove(x, y, player) for x, y in row]
        return out


class TicTacToe(alphabeta.StrategyGame):
    FIELD_SIZE = (3, 3)
    FIELD_CLASS = TicTacToeField
    DIFFICULTIES = {
        "Ea": (GREEN, 1, 1),
        "Me": (YELLOW, 1, 2),
        "Di": (RED, 5, 9)
    }

if __name__ == "__main__":
    field = TicTacToeField()
    random.shuffle(field.ORDER[0])
    random.shuffle(field.ORDER[1])
    random.shuffle(field.ORDER[2])

    ab = alphabeta.AlphaBeta(10, 100)
    player = field.COLOR1
    while not field.game_over():
        print(field)
        if player == field.COLOR2:
            move = ab(player, field)
        else:
            while True:
                try:
                    i = int(input())
                    x = (i-1) % 3
                    y = 2-(i-1)//3
                    move = TicTacToeMove(x, y, player)
                    print(move)
                    break
                except:
                    import time
                    time.sleep(1)
                    print("try again")
                    pass
        field = move.apply(field)
        player = field.other(player)
    print(field)
