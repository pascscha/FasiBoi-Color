from IO.controller import _BaseController
from pygame import KEYDOWN, KEYUP


class PygameController(_BaseController):
    def __init__(self):
        super().__init__()
        self.keymap = {
            276: self.left,  # Arrow Left
            273: self.up,  # Arrow Up
            275: self.right,  # Arrow Right
            274: self.down,  # Arrow Down
            97: self.a,  # A
            98: self.b,  # B
            27: self.menu  # Esc
        }

    def update(self, event):
        if event.type == KEYDOWN:
            if event.key in self.keymap:
                self.keymap[event.key].update(True)
        elif event.type == KEYUP:
            if event.key in self.keymap:
                self.keymap[event.key].update(False)
