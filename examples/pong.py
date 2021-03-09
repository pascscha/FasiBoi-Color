import numpy as np
import random
import time

from IO.pygame import PygameIOManager
from applications.games.pong import Pong

if __name__ == "__main__":
    fps = 20
    with PygameIOManager() as ioManager:
        ioManager.run(Pong())
