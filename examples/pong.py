from IO.gui import PygameIOManager
from applications.games.pong import Pong

if __name__ == "__main__":
    with PygameIOManager(fps=10) as ioManager:
        ioManager.run(Pong())
