import numpy as np
import random
import time

from IO import PygameIOManager, CursersIOManager
from applications import TextMenu

if __name__ == "__main__":
    with CursersIOManager() as ioManager:
        with TextMenu(["Hello", "There"], ioManager) as application:
            last = time.time()
            while application.running:
                ioManager.update()
                application.update()
                # Limit FPS
                now = time.time()
                time.sleep(max(0,1/30 - now + last))
