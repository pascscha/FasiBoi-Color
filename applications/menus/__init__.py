from applications import _BaseApplication, controllerInput

class TextMenu(_BaseApplication):
    def __init__(self, applications, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.applications = applications
        self.choice_index = 0

        self.io.controller.right.subscribe(self.nextChoice)
        self.io.controller.left.subscribe(self.previousChoice)
    
    @controllerInput
    def nextChoice(self, button, value):
        if val:
            self.choice_index += 1

    @controllerInput
    def previousChoice(self, button, value):
        if val:
            self.choice_index -= 1

    def update(self):
        pass#print(self.choice_index)