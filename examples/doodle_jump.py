from IO.pygame import PygameIOManager
from applications.games.doodle_jump import DoodleJump

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(DoodleJump())
