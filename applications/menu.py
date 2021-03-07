from applications import core
import utils

class Menu(core.Application):
    def __init__(self, applications, *args, speed=0.01, **kwargs):
        super().__init__(*args, **kwargs)
        self.applications = applications
        self.choice_index = 0
        self.choice_current = 0
        self.speed = speed

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

    def update(self):
        diff = self.choice_index - self.choice_current
        if abs(diff) > len(self.applications)/2:
            diff -= len(self.applications)
        if abs(diff) > self.speed:
            diff = self.speed if diff > 0 else -self.speed
        
        self.choice_current += diff

        choice_1 = int(self.choice_current-1)%len(self.applications)
        choice_2 = int(self.choice_current)
        choice_3 = int(self.choice_current+1)%len(self.applications)

        progression = self.choice_current - choice_2

        bmp = utils.getTextBitmap(" ".join([
            self.applications[choice_1][:2],
            self.applications[choice_2][:2],
            self.applications[choice_3][:2]
        ]))
        
        utils.applyBitmap(bmp, self.io.display, (int(-11 + progression * -12),0), color0=(0,0,0), color1=(64,64,64))
        self.io.display.refresh()