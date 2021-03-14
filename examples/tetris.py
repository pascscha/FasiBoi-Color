from IO.pygame import PygameIOManager
from applications.games.tetris import Tetris

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Tetris())
