from applications import core
from helpers import textutils, bitmaputils
import colorsys


class Game(core.Application):
    PRE_GAME = 0
    MID_GAME = 1
    GAME_OVER = 2

    DEFAULT_SCORE = 0
    MISERE = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.highscore = self.load_value(
            "highscore", default=self.DEFAULT_SCORE)
        self.score = None

        # The state of the game, used for the STATE machine
        self.state = self.PRE_GAME

        # Can be used for any pulsing elements, such as the food of snake
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

    def reset(self, io):
        """Method called when a new game is started. Set up new game here.

        Args:
            io (IO.core.IOManager): The IO manager that the application is running in
        """
        pass

    @staticmethod
    def score_str(score):
        if int(score) == score:
            return str(int(score))
        elif score >= 10:
            return str(int(score))
        elif score >= 1:
            return str(round(score, 1))
        else:
            return str(round(score, 2))[1:]

    def _update_pregame(self, io, delta):
        """Start screen of the game which shows highscore and last score

        Args:
            io (IO.core.IOManager): The IO manager that the application is running in
            delta (float): How much time has passed since the last frame
        """

        # Save score if its a new highscore
        if self.score is not None:
            if self.MISERE and self.score < self.highscore or not self.MISERE and self.score > self.highscore:
                self.highscore = self.score
                self.save_value("highscore", self.highscore)

        # If A is pressed we start the game
        if io.controller.button_a.fresh_release():
            self.reset(io)
            self.state = self.MID_GAME
        else:
            # Fill display with black
            io.display.fill((0, 0, 0))

            # Generate bitmap of highscore text
            highscore_bmp = textutils.get_text_bitmap(self.score_str(self.highscore))
            if self.score is None:
                # If we have no last score yet, just display highscore
                bitmaputils.apply_bitmap(
                    highscore_bmp,
                    io.display,
                    (io.display.width //
                     2 -
                     highscore_bmp.shape[1] //
                     2,
                     io.display.height //
                     2 -
                     highscore_bmp.shape[0] //
                     2),
                    fg_color=(
                        255,
                        255,
                        255))
            else:
                # Otherwise also show last score
                score_bmp = textutils.get_text_bitmap(self.score_str(self.score))

                # Draw highscore
                bitmaputils.apply_bitmap(
                    highscore_bmp,
                    io.display,
                    (io.display.width //
                     2 -
                     highscore_bmp.shape[1] //
                     2,
                     4 -
                     highscore_bmp.shape[0] //
                     2),
                    fg_color=(
                        255,
                        255,
                        0))

                # Make color rainbow if its a new highscore
                if self.score == self.highscore:
                    score_hue = self.pulse_progression - \
                        int(self.pulse_progression)
                    score_color = tuple(
                        map(lambda x: int(x * 255), colorsys.hsv_to_rgb(score_hue, 1, 1)))
                else:
                    score_color = (0, 0, 255)

                # Draw last score
                bitmaputils.apply_bitmap(
                    score_bmp,
                    io.display,
                    (io.display.width // 2 -
                     score_bmp.shape[1] // 2, 10 - score_bmp.shape[0] // 2),
                    fg_color=score_color)

    def _update_midgame(self, io, delta):
        """The actual gameplay when the game is running. Put your game code here.

        Args:
            io (IO.core.IOManager): The IO manager that the application is running in
            delta (float): How much time has passed since the last frame
        """
        raise NotImplementedError("Please Implement this Method!")

    def _update_gameover(self, io, delta):
        """The screen shown when the game is over. Put death animations here. If
        this method is not implemented it will automatically go to the pregame screen.

        Args:
            io (IO.core.IOManager): The IO manager that the application is running in
            delta (float): How much time has passed since the last frame
        """
        self.state = self.PRE_GAME
