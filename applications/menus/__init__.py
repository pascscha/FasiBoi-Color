from applications import _BaseApplication

class TextMenu():
    def __init__(self, applications, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.applications = applications
        self.choice_index = 0
    
    def nextChoice(self, button, value):
        if val:
            self.choice_index += 1
        