from cv2 import INTER_NEAREST
#from IO.led import LEDIOManager
from IO.gui import PygameIOManager
from IO.commandline import CursesIOManager
from applications.settings import BrightnessSlider, FPSChoice, ColorPaletteChoice
from applications.menu import Menu
from applications.filebrowser import Filebrowser
from applications.animations import SolidColor, VideoPlayer
from applications.paint import Paint
from applications.games.snake import Snake
from applications.games.flappy import Flappy
from applications.games.pong import Pong
from applications.clock import Clock
from applications.games.tetris import Tetris
from applications.games.pacman import Pacman
from applications.games.tictactoe import TicTacToe
from applications.games.connect4 import Connect4
from applications.games.reversi import Reversi
from applications.games.frat import Frat
from applications.games.g2048 import G2048
from applications.games.maze import Maze
from applications.games.sudoku import Sudoku
#from applications.games.pushy import Pushy
from applications.milkdrop import Milkdrop
from applications.colors import Colors

if __name__ == "__main__":
    settings = [
        BrightnessSlider(start=0.1, end=1, default=1, name="Brightness"),
        FPSChoice(default=30, name="FPS"),
        ColorPaletteChoice()
    ]

    with PygameIOManager(record_path="file_browser.mp4") as ioManager:

        # Hack, this makes sure settings are loaded even without opening them,
        # by letting them run for 1 frame
        for setting in settings:
            setting.update(ioManager, 0)

        ioManager.run(Menu([
            Menu([
                Menu([
                    Snake(color=(11, 200, 93)),
                    Flappy(color=(116, 190, 46)),
                    Pong(color=(0, 0, 255)),
                    Tetris(color=(255, 127, 0)),
                    Pacman(color=(255, 255, 0)),
                    G2048(name="20"),
                    Frat(),
                    Maze(),
                    #Pushy(),
                    Menu([
                        TicTacToe(),
                        Connect4(name="C4"),
                        Reversi()
                    ], name="Strategy"),
                    Sudoku()
                ], name="Games"),
                Milkdrop(),
                Clock(),
                Filebrowser("resources/videos", name="Video"),
                Filebrowser(".", name="Files"),
                Menu([
                    Colors(),
                    SolidColor(
                        (255, 255, 255),
                        name="White"
                    ),
                    SolidColor(
                        (255, 0, 0),
                        name="Red"
                    ),
                    SolidColor(
                        (0, 255, 0),
                        name="Green"
                    ),
                    SolidColor(
                        (0, 0, 255),
                        name="Blue"
                    )
                ],
                    name="Color"),
                Paint()
            ],
                name="Applications"),
            Menu(settings,
                 name="Settings"),

        ]))
