from IO.gui import PygameIOManager
from applications.filebrowser import Filebrowser

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Filebrowser("."))
