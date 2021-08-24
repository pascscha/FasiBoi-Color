from IO.gui import PygameIOManager
from applications.animations import Webcam

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Webcam())
