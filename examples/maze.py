"""Example program to test the maze game
"""
from IO.gui import PygameIOManager
from applications.games.maze import Maze


if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Maze())
