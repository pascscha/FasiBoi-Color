from applications.games import core
from applications.animations import VideoPlayer
import random


class Pipe:
    def __init__(self, height, gap, x):
        self.height = height
        self.gap = gap
        self.x = x

    def draw(self, display, progression):
        display_x = int(self.x - progression)

        for x in range(display_x-1, display_x+1):
            if x < 0 or x >= display.width:
                continue
            for y in range(0, self.height-self.gap//2):
                display.update(x, y, (0, 255, 0))
            for y in range(self.height+(self.gap+1)//2, display.height):
                display.update(x, y, (0, 255, 0))

    def is_passed(self, progression):
        return progression > self.x

    def collides(self, x, y, progression):
        return self.x-progression-2 < x < self.x-progression and not self.height - self.gap/2 < y < self.height + self.gap/2


class Flappy(core.Game):
    def get_random_pipe(self, screen_height):
        score = self.score + len(self.pipes)
        gap = screen_height//2-min(3, score//10)
        height = random.randint(gap//2+2, screen_height-gap//2-2)
        if len(self.pipes) > 0:
            x = self.pipes[-1].x + gap
        else:
            x = 10
        return Pipe(height, gap, x)

    def reset(self, io):
        self.pipe_speed = 3
        self.pipe_progression = 0

        self.gravity = 20
        self.gravity_progression = 0
        self.y_velocity = -2
        self.y_location = 7.5

        self.score = 0
        self.pipes = []
        for i in range(10):
            self.pipes.append(self.get_random_pipe(int(io.display.width*1.5)))

    def _update_midgame(self, io, delta):
        if io.controller.up.get_fresh_value():
            self.y_velocity -= 7
            self.y_velocity = min(-10, self.y_velocity)

        self.y_velocity += self.gravity * delta
        self.y_location += self.y_velocity * delta
        self.pipe_progression += delta*self.pipe_speed

        if self.y_location > io.display.height:
            self.y_velocity = -10
            self.state = self.GAME_OVER
            return

        while len(self.pipes) > 0 and self.pipes[0].is_passed(self.pipe_progression):
            self.score += 1
            self.pipes = self.pipes[1:]
            self.pipes.append(self.get_random_pipe(io.display.height))

        for pipe in self.pipes:
            if pipe.collides(1, self.y_location, self.pipe_progression):
                self.y_velocity = -.1
                self.state = self.GAME_OVER
                return

        io.display.fill((0, 0, 0))

        for pipe in self.pipes:
            pipe.draw(io.display, self.pipe_progression)

        display_location = round(self.y_location)
        if 0 <= display_location < io.display.height:
            io.display.update(1, round(self.y_location), (255, 255, 0))

    def _update_gameover(self, io, delta):
        io.openApplication(VideoPlayer("resources/animations/flappy-death.gif", loop=False))
        self.state = self.PRE_GAME
        """
        self.y_velocity += self.gravity * delta
        self.y_location += self.y_velocity * delta

        if self.y_location > io.display.height:
            self.state = self.PRE_GAME

        io.display.fill((0, 0, 0))
        for pipe in self.pipes:
            pipe.draw(io.display, self.pipe_progression)

        display_location = round(self.y_location)
        if 0 <= display_location < io.display.height:
            io.display.update(1, round(self.y_location), (255, 0, 0))
        """