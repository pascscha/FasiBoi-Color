"""Example program to test animations
"""
from IO.gui import PygameIOManager
from applications.animations import VideoPlayer


if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(VideoPlayer("resources/videos/out.mp4"))
