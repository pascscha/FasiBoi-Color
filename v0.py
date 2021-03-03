import numpy as np
import random
import time

from IO import PygameIOManager, CursersIOManager
from animations import BeatAnimation, AnimationCycler

if __name__ == "__main__":
    ioManager = CursersIOManager()
    animations = [
        BeatAnimation(
            "resources/animations/shuffle1.npy",
            ioManager,
            beats_per_loop=1),
        BeatAnimation(
            "resources/animations/shuffle2-2.npy",
            ioManager,
            beats_per_loop=2),
        BeatAnimation(
            "resources/animations/shuffle3.npy",
            ioManager,
            beats_per_loop=2)
    ]

    cycler = AnimationCycler(ioManager, animations)

    fps = 30
    last = time.time()
    try:
        while ioManager.running:
            ioManager.update()
            cycler.update()    

            # Limit FPS
            now = time.time()
            time.sleep(max(0,1/30 - now + last))
    finally:
        ioManager.destroy()
