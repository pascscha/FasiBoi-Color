"""Example program to test animations
"""
from IO.gui import PygameIOManager
from applications.animations import BeatAnimation


if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(BeatAnimation(
            "resources/animations/shuffle1.npy",
            name="Walking",
            beats_per_loop=1))
