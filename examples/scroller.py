from IO.gui import PygameIOManager
from applications.scroller import *

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Scroller())
