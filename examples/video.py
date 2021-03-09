import numpy as np
import random
import time

from IO.pygame import PygameIOManager
from applications.animations import VideoPlayer

if __name__ == "__main__":
    fps = 20
    with PygameIOManager() as ioManager:
        ioManager.run(VideoPlayer("resources/videos/simpson2.mp4"))
