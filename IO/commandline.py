"""IO Management for command line interfaces
"""
import curses
from IO import core


class CursesController(core.Controller):
    """A Controller for command line inputs
    """

    def __init__(self):
        super().__init__()
        self.keymap = {
            106: self.button_left,  # J
            105: self.button_up,  # I
            108: self.button_right,  # L
            107: self.button_down,  # K
            97: self.button_a,  # A
            98: self.button_b,  # B
            113: self.button_menu,  # Q
            116: self.button_teppich  # T
        }

    def update(self, char):
        """
        Updates its button according to the pressed key
        Args:
            char: The character representation of the pressed key
        """
        for key, button in self.keymap.items():
            if key == char:
                button.update(True)
            else:
                button.update(False)


class CursesDisplay(core.Display):
    """A Display for within the command line
    """

    def __init__(self, win, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.win = win
        self.first = True

    def _update(self, x, y, color):
        if tuple(color) != (0, 0, 0):
            self.win.addstr(y + 2, x * 2 + 2, f"##")
        else:
            self.win.addstr(y + 2, x * 2 + 2, "  ")

    def _refresh(self):
        if self.first:
            self.win.clear()
            self.first = False
        self.win.refresh()


class CursesIOManager(core.IOManager):
    """Command Line IO Manager
    """

    def __init__(self, screen_res=(10, 15)):
        curses.initscr()

        self.win = curses.newwin(
            screen_res[1] + 4, screen_res[0] * 2 + 4, 2, 2)
        curses.noecho()
        self.win.nodelay(True)

        self.win.keypad(True)
        self.win.border(True)
        self.win.nodelay(True)
        self.win.refresh()

        controller = CursesController()
        display = CursesDisplay(self.win, *screen_res)
        super().__init__(controller, display)

    def update(self):
        """Update function that gets called every frame
        """
        self.controller.update(self.win.getch())

    def destroy(self):
        """Cleanup function that gets called after all applications are closed
        """
        curses.endwin()
