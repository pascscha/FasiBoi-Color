import pygame
import numpy as np
import random
import time

from controller import PygameController
from display import PygameDisplay
from animations import BeatAnimation

if __name__ == "__main__":
    bg_path = "resources/images/bg.png"
    title = "FasiBoi-Color"
    screen_pos = (150, 100)
    screen_size = (200, 300)
    pygame.init()

    try:
        bg_image = pygame.image.load(bg_path)

        win = pygame.display.set_mode(bg_image.get_size())
        pygame.display.set_caption(title)

        disp = PygameDisplay(win, screen_pos, screen_size, 10, 15)

        controller = PygameController()
        beatFeeler = BeatFeeler(controller.b)
        animation = BeatAnimation("resources/animations/shuffle3.npy", disp, controller)

        win.blit(bg_image, (0, 0))

        for x in range(10):
            for y in range(15):
                disp.update(x, y, (random.randint(0, 255),
                                   random.randint(0, 255), random.randint(0, 255)))

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
                else:
                    controller.update(event)
            animation.update()
            pygame.display.update()

    finally:
        pygame.quit()
