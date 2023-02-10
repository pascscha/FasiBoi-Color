from IO.led import LEDIOManager
from cv2 import INTER_NEAREST
# from IO.gui import PygameIOManager
# from IO.web import WebIOManager
from IO.commandline import CursesIOManager
from applications.settings import BrightnessSlider, FPSChoice, ChargeSlider, BatteryCapacity
from applications.menu import Menu
from applications.flashlight import Flashlight
from applications.closeall import CloseAll
from applications.filebrowser import Filebrowser
from applications.animations import SolidColor, VideoPlayer
from applications.paint import Paint
from applications.games.snake import Snake
from applications.games.flappy import Flappy
from applications.games.pong import Pong
from applications.clock import Clock
from applications.games.racer import Racer
from applications.games.tetris import Tetris
from applications.games.pacman import Pacman
from applications.games.tictactoe import TicTacToe
from applications.games.connect4 import Connect4
from applications.games.reversi import Reversi
from applications.games.frat import Frat
from applications.games.g2048 import G2048
from applications.games.maze import Maze
from applications.games.sudoku import Sudoku
from applications.games.pushy import Pushy
from applications.games.supermario import Supermario
from applications.milkdrop import Milkdrop
from applications.colors import Colors
from applications.scroller import Scroller
import argparse

import time
import traceback
import datetime
import os

def main():
    io = {
        "led": LEDIOManager,
    }

    parser = argparse.ArgumentParser(
        prog="FasiBoi",
        description="The gaming costume for Lucerne's carneval 2023 with a 10x15 screen resolution",
    )
    parser.add_argument("--io", choices=io.keys(), default="led", required=False)
    args = parser.parse_args()

    settings = [
        BrightnessSlider(start=0.1, end=1, default=1, name="Brightness"),
        FPSChoice(default=30, name="FPS"),
        ChargeSlider(name="Battery Charge"),
        BatteryCapacity(default=30, name="Battery Life", step_size=1, start=0, end=100),
        CloseAll(name="Close All", color=(255, 0, 0))
    ]

    with io[args.io](record_path="out.mp4") as ioManager:

        # Hack, this makes sure settings are loaded even without opening them,
        # by letting them run for 1 frame
        for setting in settings:
            setting.update(ioManager, 0)

        while True:
            try:

                ioManager.run(
                    Menu(
                        [
                            Menu(
                                [
                                    Menu(
                                        [
                                            Tetris(color=(255, 127, 0)),
                                            Snake(color=(11, 200, 93)),
                                            Flappy(color=(116, 190, 46), name="Flappy Bird"),
                                            Racer(color=(255, 0, 0)),
                                            Pong(color=(0, 0, 255)),
                                            Pacman(color=(255, 255, 0)),
                                            G2048(name="2048"),
                                            Maze(),
                                            Supermario(is_luigi=True),
                                            Menu(
                                                [
                                                    TicTacToe(name="Tic Tac Toe"),
                                                    Connect4(name="Connect 4"),
                                                    Reversi(name="Reversi"),
                                                ],
                                                name="Strategy",
                                            ),
                                            # Sudoku(),
                                            Pushy(),
                                            # Frat(name="Felder Raten"),
                                        ],
                                        name="Games",
                                    ),
                                    Milkdrop(name="Music Visualization"),
                                    Clock(),
                                    # Flashlight(name="Lampe", color=(255,255,255)),
                                    Scroller(),
                                    Filebrowser("resources/videos", name="Videos"),
                                    # Filebrowser(".", name="Files"),
                                    Menu(
                                        [
                                            Colors(name="Color Test"),
                                            SolidColor((255, 255, 255), name="White"),
                                            SolidColor((255, 0, 0), name="Red"),
                                            SolidColor((0, 255, 0), name="Green"),
                                            SolidColor((0, 0, 255), name="Blue"),
                                        ],
                                        name="Colors",
                                    ),
                                    Paint(),
                                ],
                                name="Apps",
                            ),
                            Menu(settings, name="Settings")
                        ]
                    )
                )

            except KeyboardInterrupt as e:
                print("Good Bye!")
                return
            except Exception as e:
                ioManager.display.show_img("resources/images/error.png")

                error = f"ERROR {datetime.datetime.now()}:\n\n{traceback.format_exc()}"

                if not os.path.exists("error.log"):
                    mode = "w+"
                else:
                    mode = "a"

                with open("errors.log", mode) as f:
                    f.write(error)
                print(error)

                time.sleep(2)

if __name__ == "__main__":
    main()
