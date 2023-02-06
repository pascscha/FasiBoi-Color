from applications import core
from applications.menu import SlidingChoice, Choice
from applications.colors import *


class CloseAll(core.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = [
            Choice(
                "Close all",
                RED,
                lambda io: (io.applications[0].destroy(), io.close_application()),
            ),
            Choice("Abort", GREEN, lambda io: io.close_application()),
        ]
        self.chooser = SlidingChoice(choices, 5)

    def update(self, io, delta):
        io.display.fill((0, 0, 0))
        self.chooser.update(io, delta)
