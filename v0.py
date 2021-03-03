import numpy as np
import random
import time

from IO import setupPygameIOManager
from animations import BeatAnimation

if __name__ == "__main__":
    ioManager = setupPygameIOManager()
    animation = BeatAnimation(
        "resources/animations/shuffle3.npy",
        ioManager,
        beats_per_loop=2)

    while ioManager.running:
        ioManager.update()
        animation.update()
