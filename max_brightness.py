import numpy as np
import random
import time

from IO.pygame import PygameIOManager
from applications.animations import BeatAnimation, AnimationCycler, SolidColor


if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(SolidColor((255, 255, 255)))
