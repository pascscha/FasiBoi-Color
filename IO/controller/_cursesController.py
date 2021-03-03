from IO.controller import _BaseController
from pynput import keyboard


class CursesController(_BaseController):
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
