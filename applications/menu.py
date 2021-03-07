from applications import core
from helpers import textutils, bitmaputils
import colorsys
import hashlib

class Menu(core.Application):
    def __init__(self, applications, *args, speed=4, **kwargs):
        super().__init__(*args, **kwargs)
        self.applications = applications
        self.choice_index = 0
        self.choice_current = 0
        self.speed = speed

    def update(self, io, delta):
        if io.controller.right.get_fresh_value():
            self.choice_index = (self.choice_index + 1) % len(self.applications)
        if io.controller.left.get_fresh_value():
            self.choice_index = (self.choice_index - 1) % len(self.applications)
        if io.controller.a.get_fresh_value():
            io.openApplication(self.applications[self.choice_index])
        
        diff = self.choice_index - self.choice_current

        if diff > len(self.applications)/2:
            diff -= len(self.applications)
        elif diff < -len(self.applications)/2:
            diff += len(self.applications)

        max_diff = delta * self.speed
        if abs(diff) > max_diff:
            diff = max_diff if diff > 0 else -max_diff
        
        self.choice_current += diff
        
        if self.choice_current >= len(self.applications):
            self.choice_current -= len(self.applications)
        if self.choice_current < 0:
            self.choice_current += len(self.applications)

        choice_1 = int(self.choice_current-1)%len(self.applications)
        choice_2 = int(self.choice_current)
        choice_3 = int(self.choice_current+1)%len(self.applications)

        progression = self.choice_current - choice_2

        bmp = textutils.getTextBitmap(" ".join([
            self.applications[choice_1].name[:2],
            self.applications[choice_2].name[:2],
            self.applications[choice_3].name[:2]
        ]))
        
        for x in range(io.display.width):
            for y in range(io.display.height):
                io.display.update(x,y,(0,0,0))

        color = self.applications[choice_2].color
        bitmaputils.applyBitmap(bmp, io.display, (int(-11 + progression * -12), io.display.height//2-2), color0=(0,0,0), color1=color)
        io.display.refresh()