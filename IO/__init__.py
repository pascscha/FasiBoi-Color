from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from IO.controller import *
from IO.display import *
from pynput import keyboard
import curses



class _IOManager:
    def __init__(self, controller, display):
        self.controller = controller
        self.display = display
        self.running = True

    def update(self):
        raise NotImplementedError("Please implement this method.")

    def destroy(self):
        pass


class PygameIOManager(_IOManager):
    def __init__(self,
                 bg_path="resources/images/bg.png",
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
        super().__init__(controller, display)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            else:
                self.controller.update(event)
        pygame.display.update()

    def destroy(self):
        pygame.quit()


class CursersIOManager(_IOManager):
    def __init__(self, screen_res=(10, 15)):
        screen = curses.initscr()

        self.win = curses.newwin(screen_res[1] + 2, screen_res[0]*2 + 2, 0, 0)
        curses.noecho()
        self.win.keypad(1)
        self.win.border(1)
        self.win.nodelay(1)
        self.win.refresh()

        controller = CursesController()
        display = CursesDisplay(self.win, *screen_res)

        self.listener = keyboard.Listener(
            on_press=lambda key: controller.update(key, True),
            on_release=lambda key: controller.update(key, False))
        self.listener.start()
        super().__init__(controller, display)

    def update(self):
        pass#self.display.update()
    
    def destroy(self):
        curses.echo()
        curses.endwin()
        self.listener.stop()
