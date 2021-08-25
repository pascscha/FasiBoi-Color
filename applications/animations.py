import time
from applications import core
import cv2


class VideoPlayer(core.Application):
    def __init__(self, path, *args, loop=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.cap = cv2.VideoCapture(path)
        self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.video_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.loop = loop
        self.progression = 0

    def get_frame(self, delta):
        self.progression += delta
        frame_index = int(self.progression * self.video_fps)
        if frame_index >= self.video_frames:
            if self.loop:
                frame_index = frame_index % self.video_frames
            else:
                return False, None
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        return self.cap.read()

    def update(self, io, delta):
        ret, frame = self.get_frame(delta)
        if ret and frame is not None:
            max_width = frame.shape[0] * io.display.width / io.display.height
            if max_width < frame.shape[1]:
                cut = int((frame.shape[1] - max_width) / 2)
                frame = frame[:, cut:-cut]

            max_height = frame.shape[1] * io.display.height / io.display.width
            if max_height < frame.shape[0]:
                cut = int((frame.shape[0] - max_height) / 2)
                frame = frame[cut:-cut, :]

            resized = cv2.resize(frame, (io.display.width, io.display.height))
            converted = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            for x in range(io.display.width):
                for y in range(io.display.height):
                    io.display.update(x, y, converted[y][x])
        else:
            io.close_application()


class Webcam(VideoPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.cap = cv2.VideoCapture(0)

    def get_frame(self, delta):
        return self.cap.read()


class SolidColor(core.Application):
    def __init__(self, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.brightness = 0
        self.last = time.time()
        self.up = True

    def update(self, io, delta):
        for x in range(io.display.width):
            for y in range(io.display.height):
                io.display.update(x, y, self.color)
