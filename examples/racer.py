from IO.gui import PygameIOManager
from applications.games.racer import Racer

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Racer())
