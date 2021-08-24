from IO.gui import PygameIOManager
from applications.games.flappy import Flappy

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Flappy())
