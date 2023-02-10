"""IO Management for led interfaces
"""
import curses

import IO.core
import IO.color
from IO import core, commandline
from IO.commandline import CursesController, CursesDisplay
from rpi_ws281x.rpi_ws281x import *

import gpiozero

# LED strip configuration:
LED_COUNT = 150  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53


class LEDDisplay(core.Display):
    """A Display for showing the output on the LED screen"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strip = Adafruit_NeoPixel(
            LED_COUNT,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL,
        )
        self.strip.begin()

    @staticmethod
    def color_correct(color):
        h, s, v = color.to_hsv()
        v = (v / 255) ** 2
        return IO.color.Color.from_hsv(h, s, v)

    def _update(self, x, y, color):
        index = y * 10 + 9 - x
        color = self.color_correct(IO.color.Color(*color))
        r, g, b = color

        if r > 0:
            r = max(1, r)
        if g > 0:
            g = max(1, g)
        if b > 0:
            b = max(1, b)

        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))

        self.strip.setPixelColor(int(index), Color(r, g, b))

    def _refresh(self):
        self.strip.show()

start_display = LEDDisplay(10, 15)
start_display.start()
del start_display

class FasiBoiController(core.Controller):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pins = {
            23: self.button_left,
            27: self.button_right,
            22: self.button_up,
            24: self.button_down,
            5: self.button_a,
            6: self.button_b,
            25: self.button_menu,
            26: self.button_teppich
        }

        self.buttons = {
            gpiozero.Button(pin, bounce_time=0.1): software_button
            for pin, software_button in self.pins.items()
        }

        for button, software_button in self.buttons.items():
            button.when_pressed = software_button.update_true
            button.when_released = software_button.update_false

    def update(self):
        for hardware_button, software_button in self.buttons.items():
            software_button.update(hardware_button.is_pressed)


class ShittyDisplay(core.Display):
    def _update(self, *args, **kwargs):
        pass

    def output_screen(self, *args, **kwargs):
        lines = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                if any([bright > 128 for bright in self.pixels[x][y]]):
                    line.append("X ")
                else:
                    line.append("  ")
            lines.append("".join(line))
        print("\n".join(lines))


class LEDIOManager(core.IOManager):
    """LED Screen IO Manager"""

    def __init__(self, *args, screen_res=(10, 15), **kwargs):
        # curses.initscr()
        # self.win = curses.newwin(screen_res[1] + 4, screen_res[0] * 2 + 4, 2, 2)

        # # curses.noecho()
        # self.win.keypad(1)
        # self.win.border(1)
        # self.win.nodelay(1)
        # self.win.refresh()

        controller = FasiBoiController()
        # display = ShittyDisplay(*screen_res)
        display = LEDDisplay(*screen_res)

        super().__init__(controller, display, *args, **kwargs)

    def update(self):
        """Update function that gets called every frame"""
        self.controller.update()
        # self.display.output_screen()
        # self.controller.update(self.win.getch())

    def destroy(self):
        """Cleanup function that gets called after all applications are closed"""
        pass
        # curses.nocbreak()
        # curses.echo()
        # curses.endwin()
