import pygame
from IO.controller import *
from IO.display import *


class _IOManager:
    def __init__(self, controller, display):
        self.controller = controller
        self.display = display
        self.running = True

    def update(self):
        raise NotImplementedError("Please implement this Method")


class PygameIOManager(_IOManager):
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            else:
                self.controller.update(event)
        pygame.display.update()


def setupPygameIOManager(bg_path="resources/images/bg.png",
                         title="FasiBoi-Color",
                         screen_pos=(150, 100),
                         screen_size=(200, 300),
                         screen_res=(10, 15)):
    pygame.init()
    pygame.display.set_caption(title)


    bg_image = pygame.image.load(bg_path)
    win = pygame.display.set_mode(bg_image.get_size())
    win.blit(bg_image, (0, 0))

    display = PygameDisplay(win, screen_pos, screen_size, *screen_res)
    controller = PygameController()

    return PygameIOManager(controller, display)
