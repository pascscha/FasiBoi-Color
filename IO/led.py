"""IO Management for led interfaces
"""
import curses

import IO.core
import IO.color
from IO import core, commandline
from IO.commandline import CursesController
from rpi_ws281x.rpi_ws281x import *

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
    """A Display for showing the output on the LED screen
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strip = Adafruit_NeoPixel(
            LED_COUNT,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL)
        self.strip.begin()

    @staticmethod
    def color_correct(color):
        h, s, v = color.to_hsv()
        v = (v/255) ** 2    
        return IO.color.Color.from_hsv(h, s, v)

    def _update(self, x, y, color):
        index = y * 10 + 9-x
        color = self.color_correct(IO.color.Color(*color))
        r,g,b = color

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


class LEDIOManager(core.IOManager):
    """LED Screen IO Manager
    """

    def __init__(self, screen_res=(10, 15)):
        curses.initscr()

        self.win = curses.newwin(
            screen_res[1] + 4, screen_res[0] * 2 + 4, 2, 2)

        #curses.noecho()
        self.win.keypad(1)
        self.win.border(1)
        self.win.nodelay(1)
        self.win.refresh()

        controller = CursesController()
        display = LEDDisplay(*screen_res)
        
        super().__init__(controller, display)

    def update(self):
        """Update function that gets called every frame
        """
        self.controller.update(self.win.getch())

    def destroy(self):
        """Cleanup function that gets called after all applications are closed
        """
        curses.nocbreak()
        curses.echo()
        curses.endwin()
