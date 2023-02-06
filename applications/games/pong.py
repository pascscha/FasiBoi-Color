from applications.games import core
import random
import math


class Pong(core.Game):
    def reset(self, io):
        self.ball_x = io.display.width / 2
        self.ball_y = io.display.height / 2
        self.ball_direction = -math.pi / 2 + (0.5 - random.random()) * math.pi / 2
        self.ball_speed = 10
        self.platform_width = io.display.width // 2
        self.platform_speed = 10
        self.ai_platform_width = io.display.width // 2
        self.ai_platform_speed = 10

        self.platform_pos = io.display.width / 2
        self.ai_platform_pos = io.display.width / 2
        self.score = 0

    def _update_midgame(self, io, delta):
        if io.controller.button_left.get_value():
            self.platform_pos -= self.platform_speed * delta
            if self.platform_pos - self.platform_width / 2 < 0:
                self.platform_pos = self.platform_width / 2
        if io.controller.button_right.get_value():
            self.platform_pos += self.platform_speed * delta
            if self.platform_pos + self.platform_width / 2 > io.display.width:
                self.platform_pos = io.display.width - self.platform_width / 2

        self.ball_x += math.cos(self.ball_direction) * self.ball_speed * delta
        self.ball_y += math.sin(self.ball_direction) * self.ball_speed * delta

        t = -(self.ball_y - 1) / math.sin(self.ball_direction)
        if t > 0:
            x0 = self.ball_x + math.cos(self.ball_direction) * t
            x = abs(x0) % (2 * (io.display.width - 1))
            if x >= io.display.width:
                x = 2 * io.display.width - x

            diff = x - self.ai_platform_pos
            if diff > self.ai_platform_speed * delta:
                diff = self.ai_platform_speed * delta
            elif diff < -self.ai_platform_speed * delta:
                diff = -self.ai_platform_speed * delta
            self.ai_platform_pos += diff
            if self.ai_platform_pos + self.ai_platform_width / 2 > io.display.width - 1:
                self.ai_platform_pos = io.display.width - 1 - self.ai_platform_width / 2
            if self.ai_platform_pos - self.ai_platform_width / 2 < 0:
                self.ai_platform_pos = self.ai_platform_width / 2

        if self.ball_x < 0:
            self.ball_x = 0
            self.ball_direction = math.pi - self.ball_direction
        elif self.ball_x > io.display.width - 1:
            self.ball_x = io.display.width - 1
            self.ball_direction = math.pi - self.ball_direction

        if 0 < self.ball_y < 1:
            if (
                self.ai_platform_pos - self.ai_platform_width / 2
                < self.ball_x
                < self.ai_platform_pos + self.ai_platform_width / 2
            ):
                self.ball_direction = (
                    math.pi / 2
                    + math.pi
                    / 2
                    * (self.ball_x - self.ai_platform_pos)
                    / self.ai_platform_width
                )
                self.ball_y = 1

        elif io.display.height - 2 < self.ball_y < io.display.height - 1:
            if (
                self.platform_pos - self.platform_width / 2 - 1
                < self.ball_x
                < self.platform_pos + self.platform_width / 2
            ):
                self.ball_direction = -(
                    math.pi / 2
                    - math.pi
                    / 2
                    * (self.ball_x - self.platform_pos)
                    / self.platform_width
                )
                self.ball_y = io.display.height - 2
                self.score += 1
                self.ball_speed += 1 / 2
                if self.score % 15 == 0:
                    self.platform_width = max(1, self.platform_width - 1)
                    self.ai_platform_width = max(1, self.ai_platform_width - 1)

        if self.ball_y < 0:
            self.ball_y = 1
            self.ball_direction *= -1

        elif self.ball_y > io.display.height - 1:
            self.state = self.GAME_OVER
            return

        io.display.fill((0, 0, 0))

        io.display.update(round(self.ball_x), round(self.ball_y), (255, 255, 255))

        for x in range(
            round(self.ai_platform_pos - self.ai_platform_width / 2),
            round(self.ai_platform_pos + self.ai_platform_width / 2),
        ):
            io.display.update(x, 0, (255, 0, 0))

        for x in range(
            round(self.platform_pos - self.platform_width / 2),
            round(self.platform_pos + self.platform_width / 2),
        ):
            io.display.update(x, io.display.height - 1, (0, 255, 0))
