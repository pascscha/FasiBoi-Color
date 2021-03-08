from applications import core
from helpers import textutils, bitmaputils
import colorsys


class Game(core.Application):
    PRE_GAME = 0
    MID_GAME = 1
    GAME_OVER = 2
    POST_GAME = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.highscore = self.load_value("highscore", default=0)
        self.last_score = None
        self.state = self.PRE_GAME

        self.pulse_progression = 0
        self.pulse_speed = 1

    def update(self, io, delta):
        self.pulse_progression += delta * self.pulse_speed

        if self.state == self.PRE_GAME:
            self._update_pregame(io, delta)
        elif self.state == self.MID_GAME:
            self._update_midgame(io, delta)
        elif self.state == self.GAME_OVER:
            self._update_gameover(io, delta)

    def reset(self):
        pass

    def _update_pregame(self, io, delta):
        if io.controller.a.get_fresh_value():
            self.reset()
            self.state = self.MID_GAME
        else:
            for x in range(io.display.width):
                for y in range(io.display.height):
                    io.display.update(x, y, (0, 0, 0))

            highscore_bmp = textutils.getTextBitmap(str(self.highscore))
            if self.last_score is None:
                bitmaputils.applyBitmap(
                    highscore_bmp,
                    io.display,
                    (io.display.width//2 -
                     highscore_bmp.shape[1]//2, io.display.height//2-highscore_bmp.shape[0]//2),
                    color0=(0, 0, 0),
                    color1=(255, 255, 255))
            else:
                score_bmp = textutils.getTextBitmap(str(self.last_score))

                bitmaputils.applyBitmap(
                    highscore_bmp,
                    io.display,
                    (io.display.width//2 -
                     highscore_bmp.shape[1]//2, 4-highscore_bmp.shape[0]//2),
                    color0=(0, 0, 0),
                    color1=(255, 255, 0))

                if self.last_score == self.highscore:
                    score_hue = self.pulse_progression - \
                        int(self.pulse_progression)
                    score_color = tuple(
                        map(lambda x: int(x*255), colorsys.hsv_to_rgb(score_hue, 1, 1)))
                else:
                    score_color = (0, 0, 255)

                bitmaputils.applyBitmap(
                    score_bmp,
                    io.display,
                    (io.display.width//2 -
                     score_bmp.shape[1]//2, 10-score_bmp.shape[0]//2),
                    color0=(0, 0, 0),
                    color1=score_color)

    def _update_midgame(self, io, delta):
        raise NotImplementedError("Please Implement this Method!")

    def _update_gameover(self, io, delta):
        self.state = self.PRE_GAME
