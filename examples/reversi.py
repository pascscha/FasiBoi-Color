from IO.pygame import PygameIOManager
from applications.games.reversi import Reversi

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Reversi())
