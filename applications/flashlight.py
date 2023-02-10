from applications import core
from IO.color import *
from helpers import textutils, bitmaputils
import datetime


class Flashlight(core.Application):
    def update(self, io, delta):
        for x in range(io.display.width):
            for y in range(io.display.height):
                io.display._update(x, y, WHITE)
        io.display._refresh()
