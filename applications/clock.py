from applications import core
from helpers import textutils, bitmaputils
import datetime


class Clock(core.Application):
    def update(self, io, delta):
        time = datetime.datetime.now()
        hour_bmp = textutils.get_text_bitmap(f"{time.hour:02}")
        minute_bmp = textutils.get_text_bitmap(f"{time.minute:02}")

        io.display.fill((0, 0, 0))
        bitmaputils.apply_bitmap(
            hour_bmp,
            io.display,
            (io.display.width // 2 - hour_bmp.shape[1] // 2,
             4 - hour_bmp.shape[0] // 2),
            fg_color=(255, 255, 255))

        bitmaputils.apply_bitmap(
            minute_bmp,
            io.display,
            (io.display.width // 2 - hour_bmp.shape[1] // 2,
             10 - hour_bmp.shape[0] // 2),
            fg_color=(255, 255, 255))
