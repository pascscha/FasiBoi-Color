from IO.controller import _BaseController


class RbpyController(_BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keymap = {
            106: self.left,  # Arrow Left
            105: self.up,  # Arrow Up
            108: self.right,  # Arrow Right
            107: self.down,  # Arrow Down
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
