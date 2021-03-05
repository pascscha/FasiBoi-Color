import numpy as np
import random
import time

from IO import PygameIOManager, CursersIOManager
from applications import _BaseApplication

if __name__ == "__main__":
    ioManager = CursersIOManager()
    try:
        application = _BaseApplication(ioManager)
        last = time.time()
        while application.running:
            ioManager.update()
            application.update()

            # Limit FPS
            now = time.time()
            time.sleep(max(0,1/30 - now + last))
    except KeyboardInterrupt:
        pass
    finally:
        ioManager.destroy()
        application.destroy()
