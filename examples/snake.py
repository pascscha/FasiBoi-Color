from IO.pygame import PygameIOManager
from applications.games.snake import Snake

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Snake())
