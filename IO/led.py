from IO import core
from rpi_ws281x.rpi_ws281x import *

import time
import argparse

# LED strip configuration:
LED_COUNT      = 149      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

class LEDDisplay(core.Display):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()

    def _update(self, x, y, color):
        #y -= 2
        if y == 13 and x <= 1:
            return
        elif y == 14:
            index = y * 10 + x - 2
        elif y %2 == 0:
            index = y * 10 + x
        else:
            index = y * 10 + 9 - x

        self.strip.setPixelColor(index, Color(*color))

    def refresh(self):
        self.strip.show()
        
class LEDController(core.Controller):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keymap = {
            106: self.left,  # J
            105: self.up,  # I
            108: self.right,  # L
            107: self.down,  # K
            97: self.a,  # A
            98: self.b,  # B
            27: self.menu  # Esc
        }

    def update(self, char):
        for key, button in self.keymap.items():
            if key == char:
                button.update(True)
            else:
                button.update(False)

class LEDIOManager(core.IOManager):
    def __init__(self, screen_res=(10, 15)):
        self.screen = curses.initscr()
        self.screen.nodelay(1)
        curses.nocbreak()

        controller = RbpyController()
        display = LEDDisplay(*screen_res, lazy=False)
        super().__init__(controller, display)

    def update(self):
        pass
        try:
            char = self.screen.getch()
            if char != -1:
                self.controller.update(char)
        except:
            pass

    def destroy(self):
        curses.endwin()