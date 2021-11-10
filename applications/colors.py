from applications import core
from IO.color import *
from helpers import textutils, bitmaputils
import datetime


class Colors(core.Application):
    def update(self, io, delta):
        for x in range(io.display.width):
            for y in range(io.display.height):
                hue = x/io.display.width
                vert_box = (io.display.height - y - 1) % io.display.height//3
                value = (1+vert_box) / (io.display.height//3)
                saturation = 1 - (y % 3)/3
                io.display.update(x, y, Color.from_hsv(hue, saturation, value))
        
        self.sleep([core.ButtonPressWaker(io.controller.button_menu)])
