from IO.pygame import PygameIOManager
from applications.animations import VideoPlayer

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(VideoPlayer("resources/videos/music.mp4"))
