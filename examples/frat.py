from IO.gui import PygameIOManager
from applications.games.frat import Frat

if __name__ == "__main__":
    with PygameIOManager(bg_path=None, screen_pos=(0, 0), screen_size=(500, 750)) as ioManager:
        ioManager.run(Frat())
