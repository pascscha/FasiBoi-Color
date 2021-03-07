import numpy as np
import random
import time

from IO.pygame import PygameIOManager
from applications.animations import BeatAnimation, AnimationCycler


if __name__ == "__main__":
    fps = 20
    with PygameIOManager() as ioManager:
        ioManager.run(BeatAnimation(
            "resources/animations/shuffle1.npy",
            name="Walking",
            beats_per_loop=1))
