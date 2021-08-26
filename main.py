from cv2 import INTER_NEAREST
from IO.gui import PygameIOManager
from applications.settings import BrightnessSlider, FPSChoice
from applications.menu import Menu
from applications.animations import SolidColor, VideoPlayer, Webcam
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
from applications.milkdrop import Milkdrop

if __name__ == "__main__":
    settings = [
        BrightnessSlider(start=0.1, end=1, default=1, name="Brightness"),
        FPSChoice(default=30, name="FPS")
    ]

    with PygameIOManager(bg_path=None, screen_pos=(0, 0), screen_size=(500, 750)) as ioManager:

        # Hack, this makes sure settings are loaded even without opening them,
        # by letting them run for 1 frame
        for setting in settings:
            setting.update(ioManager, 0)

        ioManager.run(Menu([
            Menu([
                Menu([
                    Snake(color=(11, 116, 93)),
                    Flappy(color=(116, 190, 46)),
                    Pong(color=(0, 0, 255)),
                    Tetris(color=(255, 127, 0)),
                    Pacman(color=(255, 255, 0)),
                    G2048(name="20"),
                    Frat(),
                    Maze(),
                    Menu([
                        TicTacToe(),
                        Connect4(name="C4"),
                        Reversi()
                    ], name="Strategy")
                ], name="Games"),
                Milkdrop(),
                Clock(),
                Menu([
                    VideoPlayer("resources/videos/pattern.gif", name="Pattern", interpolation=INTER_NEAREST),
                    VideoPlayer("resources/videos/eye.gif", name="Eye", interpolation=INTER_NEAREST),
                    VideoPlayer("resources/videos/walk.gif", name="Walk", interpolation=INTER_NEAREST),
                    VideoPlayer("resources/videos/spin.gif", name="Spin", interpolation=INTER_NEAREST),
                    VideoPlayer("resources/videos/evil.gif", name="Evil", interpolation=INTER_NEAREST),
                ], name="Video"),
                Webcam(),
                Menu([
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
