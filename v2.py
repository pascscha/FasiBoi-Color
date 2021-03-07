import numpy as np
import random
import time

from IO import LEDIOManager
from applications import Menu
from applications.animations import BeatAnimation, AnimationCycler


if __name__ == "__main__":
    fps = 20
    with LEDIOManager() as ioManager:
        with Menu(["12", "34", "56", "78", "90"], ioManager) as application:
            last = time.time()
            while application.running:
                ioManager.update()
                application.update()
                # Limit FPS
                now = time.time()
                time.sleep(max(0,1/fps - now + last))
