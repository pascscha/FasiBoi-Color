from IO.gui import PygameIOManager
from applications.settings import BrightnessSlider, FPSChoice
from applications.menu import Menu

if __name__ == "__main__":
    settings = [
        BrightnessSlider(default=1, name="Brightness"),
        FPSChoice(default=1, name="FPS"),
    ]

    with PygameIOManager() as ioManager:
        ioManager.run(Menu(settings))
