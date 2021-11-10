import os
from applications.animations import VideoPlayer
from applications.menu import Menu
from applications import core
from IO.color import *
from helpers import animations, textutils, bitmaputils

class Texteditor(core.Application):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.row = animations.AnimatedValue(0, speed=5)
        self.col = animations.AnimatedValue(0, speed=5)
        self.content = self.get_content()

    def get_content(self):
        with open(self.path, errors="ignore") as f:
            return f.read().split("\n")

    def update(self, io, delta):
        if io.controller.button_left.fresh_press():
            self.col.set_value(self.col.new_value - 1)

        if io.controller.button_right.fresh_press():
            self.col.set_value(self.col.new_value + 1)

        if io.controller.button_up.fresh_press():
            self.row.set_value(self.row.new_value - 1)

        if io.controller.button_down.fresh_press():
            self.row.set_value(self.row.new_value + 1)

        row = self.row.tick(delta)
        col = self.col.tick(delta)

        io.display.fill((0,0,0))

        char_bitmap = np.zeros((23, 15), dtype=np.bool)

        for x in range(4):
            for y in range(4):
                char = " "
                
                r = int(row) - 1 + y
                c = int(col) - 1 + x
                if 0 <= r < len(self.content):
                    if 0 <= c < len(self.content[r]):
                        char = self.content[r][c]
                char_bitmap[6*y:6*y+5, 4*x: 4*x+3] = textutils.get_char_bitmap(char)

        
        bitmaputils.apply_bitmap(char_bitmap, io.display,
            ((-1-int(4 * (col - int(col)))), 
            (-1-int(6 * (row - int(row)))))
        )
