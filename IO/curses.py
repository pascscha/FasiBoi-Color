import curses
from IO import core
from pynput import keyboard

class CursesController(core.Controller):
    def __init__(self):
        super().__init__()
        self.keymap = {
            keyboard.Key.left: self.left,  # Arrow Left
            keyboard.Key.up: self.up,  # Arrow Up
            keyboard.Key.right: self.right,  # Arrow Right
            keyboard.Key.down: self.down,  # Arrow Down
            "a": self.a,  # A
            "b": self.b,  # B
            keyboard.Key.esc: self.menu  # Esc
        }

    def update(self, event, pressed):
        try:
            event = event.char.lower()
        except AttributeError:
            pass

        if event in self.keymap:
            self.keymap[event].update(pressed)

class CursesDisplay(core.Display):
    def __init__(self, win, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.win = win

    def _update(self, x, y, color):
        if color == (255, 255, 255):
            self.win.addstr(y+2, x*2+2, "##")
        else:
            self.win.addstr(y+2, x*2+2, "  ")
        

class CursersIOManager(core.IOManager):
    def __init__(self, screen_res=(10, 15)):
        screen = curses.initscr()

        self.win = curses.newwin(screen_res[1] + 4, screen_res[0]*2 + 4, 2, 2)
        curses.noecho()
        self.win.keypad(1)
        self.win.border(1)
        self.win.nodelay(1)
        self.win.refresh()

        controller = CursesController()
        display = CursesDisplay(self.win, *screen_res, lazy=False)

        self.listener = keyboard.Listener(
            on_press=lambda key: controller.update(key, True),
            on_release=lambda key: controller.update(key, False))
        self.listener.start()
        super().__init__(controller, display)

    def update(self):
        self.win.refresh()

    def destroy(self):
        curses.echo()
        curses.endwin()
        self.listener.stop()