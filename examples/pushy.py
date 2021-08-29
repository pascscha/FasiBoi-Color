from IO.gui import PygameIOManager
from applications.games.pushy import Pushy

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Pushy())
