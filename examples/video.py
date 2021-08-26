from IO.gui import PygameIOManager
from applications.animations import VideoPlayer
from cv2 import INTER_NEAREST

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(VideoPlayer("resources/videos/03.gif", interpolation=INTER_NEAREST))
