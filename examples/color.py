from IO.gui import PygameIOManager
from applications.colors import Colors

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Colors())
