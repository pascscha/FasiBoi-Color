from controller import _BaseController
from pygame import KEYDOWN, KEYUP

class PygameController(_BaseController):
    def __init__(self):
        super().__init__()
        self.keymap = {
            276: self.left,
            273: self.up,
            275: self.right,
            274: self.down,
            97: self.a,
            98: self.b
        }

    def update(self, event):
        if event.type == KEYDOWN:
            if event.key in self.keymap:
                self.keymap[event.key].update(True)
        elif event.type == KEYUP:
            if event.key in self.keymap:
                self.keymap[event.key].update(False)
