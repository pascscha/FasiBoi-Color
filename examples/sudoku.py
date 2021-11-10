from IO.gui import PygameIOManager
from applications.games.sudoku import Sudoku

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Sudoku())
