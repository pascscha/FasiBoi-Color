import os
from applications.animations import VideoPlayer
from applications.texteditor import Texteditor
from applications.menu import Menu
from applications import core
from IO.color import *


class EmptyApplication(core.Application):
    def update(self, io, delta):
        io.close_application()


class Filebrowser(core.Application):
    VIDEO_ENDINGS = ["mp4", "gif", "avi", "jpg", "png"]

    def __init__(self, root, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root
        self.menu = self.refresh()

    def refresh(self):
        folders = []
        files = []
        for file in sorted(os.listdir(self.root)):
            full = os.path.join(self.root, file)
            if os.path.isdir(full):
                folders.append(
                    Filebrowser(os.path.join(self.root, file), name=file, color=BLUE)
                )
            elif file.split(".")[-1].lower() in self.VIDEO_ENDINGS:
                files.append(VideoPlayer(full, name=file, color=GREEN * 0.5))
            else:
                files.append(Texteditor(full, name=file, color=WHITE))
        return Menu(folders + files)

    def update(self, io, delta):
        return self.menu.update(io, delta)
