"""Example program to test the maze game
"""
from IO.gui import PygameIOManager
from applications.games.minesweeper import MineSweeper


if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(MineSweeper())
