from IO.pygame import PygameIOManager
from applications.games.pong import Pong

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Pong())
