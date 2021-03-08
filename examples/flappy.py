import numpy as np
import random
import time

from IO.pygame import PygameIOManager
from applications.games.flappy import Flappy

if __name__ == "__main__":
    fps = 20
    with PygameIOManager() as ioManager:
        ioManager.run(Flappy())
