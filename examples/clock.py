from IO.pygame import PygameIOManager
from applications.clock import Clock

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Clock())
