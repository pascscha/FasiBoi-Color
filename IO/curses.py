import curses
from IO import core

class CursesController(core.Controller):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keymap = {
            106: self.left,  # J
            105: self.up,  # I
            108: self.right,  # L
            107: self.down,  # K
            97: self.a,  # A
            98: self.b,  # B
            27: self.menu  # Esc
        }

    def update(self, char):
        for key, button in self.keymap.items():
            if key == char:
                button.update(True)
            else:
                button.update(False)

class CursesDisplay(core.Display):
    def __init__(self, win, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.win = win

    def _update(self, x, y, color):
        if color != (0, 0, 0):
            self.win.addstr(y+2, x*2+2, "##")
        else:
            self.win.addstr(y+2, x*2+2, "  ")
    
    def refresh(self):
        pass#self.win.refresh()


class CursesIOManager(core.IOManager):
    def __init__(self, screen_res=(10, 15)):
        screen = curses.initscr()

        self.win = curses.newwin(screen_res[1] + 4, screen_res[0]*2 + 4, 2, 2)
        curses.noecho()
        self.win.nodelay(1)

        self.win.keypad(1)
        self.win.border(1)
        self.win.nodelay(1)
        self.win.refresh()

        controller = CursesController()
        display = CursesDisplay(self.win, *screen_res, lazy=False)
        super().__init__(controller, display)

    def update(self):
        self.controller.update(self.win.getch())

    def destroy(self):
        curses.endwin()