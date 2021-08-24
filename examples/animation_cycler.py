from IO.gui import PygameIOManager
from applications.animations import BeatAnimation, AnimationCycler

if __name__ == "__main__":
    animations = [
        BeatAnimation(
            "resources/animations/shuffle1.npy",
            beats_per_loop=1),
        BeatAnimation(
            "resources/animations/shuffle2-2.npy",
            beats_per_loop=2),
        BeatAnimation(
            "resources/animations/shuffle3.npy",
            beats_per_loop=2)
    ]

    with PygameIOManager() as ioManager:
        ioManager.run(AnimationCycler(animations))
