from IO.display import _BaseDisplay

class CursesDisplay(_BaseDisplay):
    def __init__(self, win, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.win = win

    def _update(self, x, y, color):
        if color == (255, 255, 255):
            self.win.addstr(y+1, x*2+1, "##")
        else:
            self.win.addstr(y+1, x*2+1, "  ")
        self.win.refresh()
        