from applications import core
from helpers import textutils, bitmaputils, animations
from applications.colors import *
from datetime import datetime
import time


class Choice:
    def __init__(self, text, color, fun):
        self.text = text
        self.color = color
        self.fun = fun


class SlidingChoice:
    def __init__(self, choices, height=8, speed=4, text_speed=10):
        self.choices = choices
        self.bmps = [textutils.get_text_bitmap(choice.text) for choice in self.choices]
        self.index = animations.AnimatedValue(0, speed=speed)
        self.text_speed = text_speed
        self.scroll_offset = animations.AnimatedValue(0, speed=self.text_speed)
        self.prog = 0
        self.color = (0, 0, 0)

    def update(self, io, delta):
        if io.controller.button_up.fresh_press():
            new_value = max(0, self.index.new_value - 1)
            if self.index.get_value() != new_value:
                self.scroll_offset = animations.AnimatedValue(0)
            self.index.set_value(new_value)
        if io.controller.button_down.fresh_press():
            new_value = min(len(self.choices) - 1, self.index.new_value + 1)
            if self.index.get_value() != new_value:
                self.scroll_offset = animations.AnimatedValue(0)
            self.index.set_value(new_value)

        self.prog = self.index.tick(delta)

        if io.controller.button_a.fresh_release() or io.controller.button_right.fresh_release():
            self.choices[round(self.prog)].fun(io)

        for i, bmp in enumerate(self.bmps):
            if i == round(self.prog):
                color = self.choices[i].color
                textlen = self.bmps[round(self.prog)].shape[1]
                if textlen > io.display.width:
                    animlen = textlen + io.display.width + 10
                    self.scroll_offset.set_value(animlen)
                    self.scroll_offset.speed = self.text_speed / animlen
                    offset = max(0, int(self.scroll_offset.tick(delta)) - 10)
                    if offset >= textlen:
                        x = 1 + io.display.width - (offset - textlen)
                    else:
                        x = 1 - int(offset)

                    if offset == textlen + io.display.width:  # restart scroll
                        self.scroll_offset = animations.AnimatedValue(0)
                else:
                    x = 1
            else:
                color = Color(*self.choices[i].color) * 0.5
                x = 1
            bitmaputils.apply_bitmap(
                bmp,
                io.display,
                (x, io.display.height // 2 - 2 + 6 * i - round(6 * self.prog)),
                fg_color=color,
            )


class ApplicationOpener:
    def __init__(self, application):
        self.application = application

    def __call__(self, io):
        io.open_application(self.application)


class Menu(core.Application):
    def __init__(self, applications, *args, speed=4, **kwargs):
        super().__init__(*args, **kwargs)
        self.applications = applications
        self.speed = speed
        choices = [
            Choice(application.name, application.color, ApplicationOpener(application))
            for application in applications
        ]
        self.chooser = SlidingChoice(choices, 5, speed=self.speed)
        self.bat = 1

    def update(self, io, delta):
        io.display.fill((0, 0, 0))

        if io.controller.button_left.fresh_release():
            io.close_application()

        # Text
        self.chooser.update(io, delta)

        # Battery
        battery = io.get_battery()

        if battery < 0.5:
            battery_color = animations.blend_colors(RED, YELLOW * 0.5, battery * 2)
        else:
            battery_color = animations.blend_colors(
                YELLOW * 0.5, GREEN * 0.5, (battery - 0.5) * 2
            )

        for x in range(1 + round((io.display.width - 1) * battery)):
            io.display.update(x, 0, battery_color)
        for x in range(1 + round((io.display.width - 1) * battery), io.display.width):
            io.display.update(x, 0, BLACK)


        # Clock
        now = datetime.now()
        hour = f"{now.hour%12:04b}"
        minute = f"{now.minute:06b}"
        for x in range(4):
            if hour[x] == "1":
                io.display.update(x, io.display.height - 1, (RED + 0.5 * GREEN) * 0.5)
            else:
                io.display.update(x, io.display.height - 1, (RED + 0.5 * GREEN) * 0.0)

        for x in range(6):
            if minute[x] == "1":
                io.display.update(
                    io.display.width - 6 + x, io.display.height - 1, BLUE * 0.5
                )
            else:
                io.display.update(
                    io.display.width - 6 + x, io.display.height - 1, BLUE * 0.0
                )

        if self.chooser.prog == self.chooser.index:
            self.sleep(
                [
                    core.ButtonReleaseWaker(io.controller.button_a),
                    core.ButtonPressWaker(io.controller.button_left),
                    core.ButtonPressWaker(io.controller.button_right),
                ]
            )

        # Fade Effect
        io.display.pixels[:, 1] = io.display.pixels[:, 1] * 0.25
        io.display.pixels[:, 2] = io.display.pixels[:, 2] * 0.75

        io.display.pixels[:, io.display.height - 2] = (
            io.display.pixels[:, io.display.height - 2] * 0.25
        )
        io.display.pixels[:, io.display.height - 3] = (
            io.display.pixels[:, io.display.height - 3] * 0.75
        )

    def destroy(self):
        for application in self.applications:
            application.destroy()
        self.chooser = SlidingChoice(self.chooser.choices, 5, speed=self.speed)
