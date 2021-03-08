from applications import core
import random
import json
import os
from helpers import textutils, bitmaputils
import colorsys


class Snake(core.Application):
    PRE_GAME = 0
    MID_GAME = 1
    GAME_OVER = 2
    POST_GAME = 3

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.highscore = self.load_value("highscore", default=0)

        self.pulse_progression = 0
        self.pulse_speed = 1

        self.state = self.PRE_GAME
        self.last_score = None

    def random_food_location(self):
        location = (random.randint(0, 9), random.randint(0, 14))
        while location in self.snake:
            location = (random.randint(0, 9), random.randint(0, 14))
        return location

    def update(self, io, delta):
        self.pulse_progression += delta * self.pulse_speed

        if self.state == self.PRE_GAME:
            self.update_pregame(io, delta)
        elif self.state == self.MID_GAME:
            self.update_midgame(io, delta)
        elif self.state == self.GAME_OVER:
            self.update_gameover(io, delta)

    def update_pregame(self, io, delta):
        if io.controller.a.get_fresh_value():
            self.button_press_queue = []
            self.snake = [(5, 5), (4, 5), (3, 5)]
            self.direction = self.RIGHT

            self.food = self.random_food_location()

            self.snake_progression = 0
            self.snake_speed = 3

            self.state = self.MID_GAME
            return
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

    def update_gameover(self, io, delta):
        self.snake_progression += delta * 7
        if self.snake_progression > 1:
            self.snake_progression -= 1
            if len(self.snake) > 0:
                self.snake = self.snake[1:]
            else:
                self.state = self.PRE_GAME
                return

        for x in range(io.display.width):
            for y in range(io.display.height):
                if (x, y) in self.snake:
                    io.display.update(x, y, (116, 11, 11))
                else:
                    io.display.update(x, y, (0, 0, 0))

    def update_midgame(self, io, delta):
        if io.controller.left.get_fresh_value():
            self.button_press_queue.append(self.LEFT)
        if io.controller.right.get_fresh_value():
            self.button_press_queue.append(self.RIGHT)
        if io.controller.up.get_fresh_value():
            self.button_press_queue.append(self.UP)
        if io.controller.down.get_fresh_value():
            self.button_press_queue.append(self.DOWN)

        pulser = abs(self.pulse_progression -
                     int(self.pulse_progression) - 0.5)*2

        self.snake_progression += delta * self.snake_speed
        if self.snake_progression > 1:
            self.snake_progression -= 1

            if len(self.button_press_queue) > 0:
                direction = self.button_press_queue[0]
                self.button_press_queue = self.button_press_queue[1:]
                if direction[0] != -self.direction[0] or direction[1] != -self.direction[1]:
                    self.direction = direction

            new_x = self.snake[0][0] + self.direction[0]
            if new_x >= io.display.width:
                new_x -= io.display.width
            if new_x < 0:
                new_x += io.display.width

            new_y = self.snake[0][1] + self.direction[1]
            if new_y >= io.display.height:
                new_y -= io.display.height
            if new_y < 0:
                new_y += io.display.height

            new_head = (new_x, new_y)
            if new_head in self.snake:
                self.last_score = len(self.snake)
                if self.last_score > self.highscore:
                    self.highscore = self.last_score
                    self.save_value("highscore", self.highscore)
                self.state = self.GAME_OVER
                return

            if new_head == self.food:
                self.food = self.random_food_location()
                self.snake_speed += 0.1
                self.snake = [new_head] + self.snake
            else:
                self.snake = [new_head] + self.snake[:-1]

        for x in range(io.display.width):
            for y in range(io.display.height):
                if (x, y) == self.food:
                    brightness = int(pulser * 255)
                    io.display.update(x, y, (brightness, 0, 0))
                elif (x, y) in self.snake:
                    io.display.update(x, y, (11, 116, 93))
                else:
                    io.display.update(x, y, (0, 0, 0))
        io.display.refresh()
