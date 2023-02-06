from IO.gui import PygameIOManager
from applications.milkdrop import Milkdrop

if __name__ == "__main__":
    with PygameIOManager(
        bg_path=None, screen_pos=(0, 0), screen_size=(500, 750), record_path="milkdrop.mp4"
    ) as ioManager:
        ioManager.run(Milkdrop())
