from IO.pygame import PygameIOManager
from applications.settings import BrightnessSlider, FPSChoice
from applications.menu import Menu
from applications.animations import AnimationCycler, BeatAnimation, SolidColor
from applications.paint import Paint
from applications.games.snake import Snake

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Menu([
            Menu([
                BrightnessSlider(default=1, name="Brightness"),
                FPSChoice(default=1, name="FPS")
            ],
                name="Settings"),
            Menu([
                Menu([
                    Snake()
                ],name="Games"),
                AnimationCycler([
                    BeatAnimation(
                        "resources/animations/shuffle1.npy",
                        beats_per_loop=1,
                        name="Moonwalk"),
                    BeatAnimation(
                        "resources/animations/shuffle2-2.npy",
                        beats_per_loop=2,
                        name="Charleston"),
                    BeatAnimation(
                        "resources/animations/shuffle3.npy",
                        beats_per_loop=2,
                        name="Little Big")
                ]),
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
        ]))
