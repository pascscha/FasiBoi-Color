from applications import _BaseApplication, controllerInput
import utils

class Menu(_BaseApplication):
    def __init__(self, applications, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.applications = applications
        self.choice_index = 0

        self.io.controller.right.subscribe(self.nextChoice)
        self.io.controller.left.subscribe(self.previousChoice)
            
    @controllerInput
    def nextChoice(self, value):
        if value:
            self.choice_index = (self.choice_index + 1) % len(self.applications)

    @controllerInput
    def previousChoice(self, value):
        if value:
            self.choice_index = (self.choice_index - 1) % len(self.applications)

    def update(self):
        bmp = utils.getTextBitmap(self.applications[self.choice_index][:2])
        utils.applyBitmap(bmp, self.io.display, (2,2), color0=(0,0,0), color1=(255,255,255))
