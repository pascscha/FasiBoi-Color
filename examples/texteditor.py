from IO.gui import PygameIOManager
from applications.texteditor import Texteditor

if __name__ == "__main__":
    with PygameIOManager() as ioManager:
        ioManager.run(Texteditor("examples/texteditor.py"))
