import time
from applications import core
import cv2


class VideoPlayer(core.Application):
    def __init__(self, path, *args, loop=True, interpolation=cv2.INTER_LINEAR,**kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.cap = cv2.VideoCapture(path)
        self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.MAX_FPS = self.video_fps
        self.video_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.loop = loop
        self.progression = 0
        self.last_frame = -1
        self.read = None
        self.interpolation = interpolation

    def get_frame(self, delta):
        self.progression += delta
        frame_index = int(self.progression * self.video_fps)
        if frame_index >= self.video_frames:
            if self.loop:
                frame_index = frame_index % self.video_frames
            else:
                return False, None

        if frame_index != self.last_frame or self.read is None:
            self.last_frame = frame_index
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            self.read = self.cap.read()

        #self.sleep([core.TimeWaker(1/self.video_fps)])
        return self.read

    def update(self, io, delta):
        ret, frame = self.get_frame(delta)
        if ret and frame is not None:

            max_width = frame.shape[0] * io.display.width / io.display.height
            if max_width < frame.shape[1]:
                cut = int((frame.shape[1] - max_width) / 2)
                if cut > 0:
                    frame = frame[:, cut:-cut]

            max_height = frame.shape[1] * io.display.height / io.display.width
            if max_height < frame.shape[0]:
                cut = int((frame.shape[0] - max_height) / 2)
                if cut > 0:
                    frame = frame[cut:-cut, :]

            resized = cv2.resize(frame, (io.display.width, io.display.height), interpolation=self.interpolation)
            converted = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

            io.display.pixels = converted.transpose(1, 0, 2)


        elif self.video_frames < 0:
            self.progression = 0
            self.cap.release()
            self.cap = cv2.VideoCapture(self.path)

        elif not self.loop:
            io.close_application()

    def destroy(self):
        self.cap = cv2.VideoCapture(self.path)
        self.progression = 0
        self.last_frame = -1
        self.read = None


class Webcam(VideoPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.cap = cv2.VideoCapture(0)

    def get_frame(self):
        return self.cap.read()


class SolidColor(core.Application):
    def __init__(self, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color

    def update(self, io, delta):
        io.display.fill(self.color)
        self.sleep([core.ButtonPressWaker(io.controller.button_menu)])