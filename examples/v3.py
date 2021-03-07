import numpy as np
import random
import time

from IO.curses import CursesIOManager
from applications.animations import BeatAnimation, AnimationCycler


if __name__ == "__main__":
    with CursesIOManager() as ioManager:
     
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
        with AnimationCycler(animations, ioManager) as application:
            last = time.time()
            while application.running:
                ioManager.update()
                application.update()
                # Limit FPS
                now = time.time()
                time.sleep(max(0,1/30 - now + last))
