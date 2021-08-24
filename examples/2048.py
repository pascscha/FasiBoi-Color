"""Example program to test 2048 Game
"""

from IO.gui import PygameIOManager
from applications.games.g2048 import G2048

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(G2048())
