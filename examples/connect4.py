from IO.pygame import PygameIOManager
from applications.games.connect4 import Connect4

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Connect4())
