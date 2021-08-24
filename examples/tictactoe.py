from IO.gui import PygameIOManager
from applications.games.tictactoe import TicTacToe

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(TicTacToe())
