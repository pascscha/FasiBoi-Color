from IO.gui import PygameIOManager
from applications.games.supermario import Supermario

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Supermario(is_luigi=True))
