import numpy as np
import random
import time

from IO.pygame import PygameIOManager
from applications.animations import BeatAnimation
from applications.menu import Menu

if __name__ == "__main__":
    animations = [
        BeatAnimation(
            "resources/animations/shuffle1.npy",
            name="Shuffle",
            beats_per_loop=1),
        BeatAnimation(
            "resources/animations/shuffle2-2.npy",
            name="Charleston",
            beats_per_loop=2),
        BeatAnimation(
            "resources/animations/shuffle3.npy",
            name="Little Big",
            beats_per_loop=2)
    ]

    with PygameIOManager() as ioManager:
        ioManager.run(Menu(animations))
