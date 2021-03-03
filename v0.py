import numpy as np
import random
import time

from IO import setupPygameIOManager
from animations import BeatAnimation, AnimationCycler

if __name__ == "__main__":
    ioManager = setupPygameIOManager()
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

    while ioManager.running:
        ioManager.update()
        cycler.update()
