from IO.gui import PygameIOManager
from applications.games.pacman import Pacman

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Pacman())
