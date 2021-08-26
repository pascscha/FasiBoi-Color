from applications import core
from helpers import textutils, bitmaputils


class Choice:
    def __init__(self, text, color, fun):
        self.text = text
        self.color = color
        self.fun = fun


class SlidingChoice:
    def __init__(self, choices, height, speed=4):
        self.choices = choices
        self.index = 0
        self.prog = 0
        self.speed = speed
        self.height = height
        self.color = (255, 255, 255)

    def update(self, io, delta):
        if io.controller.button_right.fresh_press():
            self.index = (self.index + 1) % len(self.choices)
        if io.controller.button_left.fresh_press():
            self.index = (self.index - 1) % len(self.choices)
        if io.controller.button_a.fresh_release():
            self.choices[self.index].fun(io)

        diff = self.index - self.prog
        if diff > len(self.choices) / 2:
            diff -= len(self.choices)
        elif diff < -len(self.choices) / 2:
            diff += len(self.choices)

        max_diff = delta * self.speed
        if abs(diff) > max_diff:
            diff = max_diff if diff > 0 else - max_diff

        self.prog += diff

        if self.prog >= len(self.choices):
            self.prog -= len(self.choices)
        if self.prog < 0:
            self.prog += len(self.choices)

        choice_1 = int(self.prog - 1) % len(self.choices)
        choice_2 = int(self.prog)
        choice_3 = int(self.prog + 1) % len(self.choices)

        progression = self.prog - choice_2

        bmp = textutils.get_text_bitmap(" ".join([
            self.choices[choice_1].text[:2],
            self.choices[choice_2].text[:2],
            self.choices[choice_3].text[:2]
        ]))

        if progression == 0:
            self.color = self.choices[choice_2].color
        else:
            color1 = self.choices[choice_2].color
            color2 = self.choices[choice_3].color
            self.color = tuple(map(
                lambda c: c[0] * (1 - progression) + c[1] * progression, zip(color1, color2)))
        bitmaputils.apply_bitmap(bmp,
                                 io.display,
                                 (int(-11 + progression * -12),
                                 self.height),
                                 fg_color=self.color)


class ApplicationOpener:
    def __init__(self, application):
        self.application = application

    def __call__(self, io):
        io.open_application(self.application)


class Menu(core.Application):
    def __init__(self, applications, *args, speed=4, **kwargs):
        super().__init__(*args, **kwargs)
        self.applications = applications
        choices = [
            Choice(
                application.name,
                application.color,
                ApplicationOpener(application)) for application in applications]
        self.chooser = SlidingChoice(choices, 5)
        self.choice_index = 0
        self.choice_current = 0
        self.speed = speed

    def update(self, io, delta):
        io.display.fill((0, 0, 0))
        self.chooser.update(io, delta)
        color = self.chooser.color
        for x in range(io.display.width):
            for y in [0, io.display.height - 1]:
                io.display.update(x, y, color)
