from IO.gui import PygameIOManager
from applications.paint import Paint

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Paint())
