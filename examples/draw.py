from IO.gui import PygameIOManager
from applications.drawings import ExampleDrawing

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(ExampleDrawing())
