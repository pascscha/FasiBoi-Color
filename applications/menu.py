from applications import core
from helpers import textutils, bitmaputils
import colorsys
import hashlib

class Menu(core.Application):
    def __init__(self, applications, *args, speed=0.01, **kwargs):
        super().__init__(*args, **kwargs)
        self.applications = applications
        self.choice_index = 0
        self.choice_current = 0
        self.speed = speed
        self.child = None

        self.io.controller.right.subscribe(self.nextChoice)
        self.io.controller.left.subscribe(self.previousChoice)
            
    @core.controllerInput
    def nextChoice(self, value):
        if value:
            self.choice_index = (self.choice_index + 1) % len(self.applications)

    @core.controllerInput
    def previousChoice(self, value):
        if value:
            self.choice_index = (self.choice_index - 1) % len(self.applications)

    @core.controllerInput
    def choose(self, value):
        pass
    
    def update(self):
        diff = self.choice_index - self.choice_current
        if diff > len(self.applications)/2:
            diff -= len(self.applications)
        elif diff < -len(self.applications)/2:
            diff += len(self.applications)
        if abs(diff) > self.speed:
            diff = self.speed if diff > 0 else -self.speed
        
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
        
        hue = int(hashlib.md5(self.applications[choice_2].name.encode()).hexdigest(),16)%255
        color = tuple(map(lambda x:int(x*255),colorsys.hsv_to_rgb(hue/255, 1, 1)))

        bitmaputils.applyBitmap(bmp, self.io.display, (int(-11 + progression * -12), self.io.display.height//2-2), color0=(0,0,0), color1=color)
        self.io.display.refresh()