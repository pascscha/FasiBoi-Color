"""Base classes for strategy games with opponents
"""
from applications.games import core
from applications.menu import SlidingChoice, Choice
from IO.color import *


class Applyer:
    """Sorry for this ugly thing, it was necessary to get around some list-comprehension issues I had"""

    def __init__(self, game, level):
        self.game = game
        self.level = level

    def __call__(self, *args, **kwargs):
        self.game.start_level(self.level)


class Puzzle(core.Game):
    """Base class for Puzzle Game with multiple levels"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_level = self.load_value("current_level", default=0)
        self.levels = self.load_value("levels", default=[])

        order = list(range(self.current_level, len(self.levels))) + list(
            range(self.current_level)
        )

        self.levelChoice = SlidingChoice(
            [Choice(f"{i+1:02}", WHITE, Applyer(self, i)) for i in order], 5
        )

    def start_level(self, level):
        self.save_value("current_level", level)
        self.current_level = level
        self.state = self.MID_GAME

    def next_level(self, level):
        self.levelChoice.index = (level + 1) % len(self.levels)
        self.state = self.PRE_GAME

    def _update_pregame(self, io, delta):
        """Displays a player select screen"""
        io.display.fill((0, 0, 0))
        self.levelChoice.update(io, delta)
        if self.state == self.MID_GAME:
            self.reset(io)
