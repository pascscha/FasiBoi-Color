from applications.games import core
import random
from helpers import textutils, bitmaputils
import math
from IO.color import *

class Tile:
    COLORS = [
        (238, 218, 197),
        (239, 171, 159),
        (234, 128, 28),
        (243, 86, 0),
        (248, 32, 0),
        (242, 40, 0),
        (231, 182, 0),
        (237, 176, 0),
        (235, 178, 0),
        (229, 174, 0),
        (232, 167, 0),
        (238, 228, 218),  # 2
        (239, 205, 199),  # 4
        (234, 181, 131),  # 8
        (243, 151, 100),  # 16
        (248, 121, 102),  # 32
        (242, 97, 68),  # 64
        (231, 206, 113),  # 128
        (237, 203, 103),  # 256
        (235, 199, 85),  # 512
        (229, 195, 85),  # 1024
        (232, 190, 82)  # 2048
        # TODO
    ]
    SPEED = 12

    def __init__(self, value, pos):
        self.value = value
        self.x, self.y = pos
        self.direction = (0, 0)
        self.fresh = True
        self.move_progression = 0

    def move(self, direction):
        self.direction = direction
        self.fresh = False
        self.move_progression = 0

    def get_colors(self):
        color_bright = self.COLORS[min(self.value - 1, len(self.COLORS) - 1)]
        color_dark = tuple(map(lambda n: n * 0.5, color_bright))

        out = []
        mask = 1
        for i in range(4):
            if self.value & mask != 0:
                out.append(color_dark)
            else:
                out.append(color_bright)
            mask = mask << 1
        return out

    def update(self, field, delta):
        score_increment = 0
        if self.direction != (0, 0):
            self.move_progression += delta * self.SPEED

            if self.move_progression >= 0:
                nx = self.x + self.direction[0]
                ny = self.y + self.direction[1]

                if nx < 0 or nx >= 4 or ny < 0 or ny >= 4:
                    self.direction = (0, 0)
                    self.move_progression = 0
                elif field[nx][ny] is None:
                    field[self.x][self.y] = None
                    field[nx][ny] = self
                    self.x = nx
                    self.y = ny
                    self.move_progression -= 1
                elif field[nx][ny].value == self.value and not field[nx][ny].fresh:
                    field[self.x][self.y] = None
                    field[nx][ny] = self
                    self.value += 1
                    score_increment = self.value
                    self.x = nx
                    self.y = ny
                    self.fresh = True
                    self.direction = (0, 0)
                else:
                    self.direction = (0, 0)
                    self.move_progression = 0
        return score_increment

    def draw(self, display):
        colors = self.get_colors()
        for x in range(2):
            for y in range(2):
                prog = min(0, max(-1, self.move_progression))
                draw_x = int(1 + self.x * 2 + x) + int(2 * self.direction[0] * prog)
                draw_y = int(display.height - 9 + self.y * 2 + y) + int(
                    2 * self.direction[1] * prog
                )
                if 0 <= draw_x < display.width and 0 <= draw_y < display.height:
                    display.update(draw_x, draw_y, colors[x + y * 2])


class G2048(core.Game):
    RANGES = {
        1: (3, -1, -1),
        -1: (1, 4),
        0: (0, 4),
    }

    def reset(self, io):
        self.field = [[None] * 4 for _ in range(4)]
        self.spawn_random()
        self.score = 1
        self.direction = (0, 0)
        self.last_field = self.copy_field(self.field)
        self.direction_queue = []

        self.update_xrange = (0, 4)
        self.update_yrange = (0, 4)

    @staticmethod
    def copy_field(field):
        return [[f for f in row] for row in field]

    @staticmethod
    def field_eq(field1, field2):
        for row1, row2 in zip(field1, field2):
            for f1, f2 in zip(row1, row2):
                if f1 != f2:
                    return False
        return True

    def is_full(self):
        for x in range(4):
            for y in range(4):
                if self.field[x][y] is None:
                    return False
        return True

    def is_game_over(self):
        if not self.is_full():
            return False
        else:
            for x in range(4):
                for y in range(1, 3):
                    if self.field[x][y].value == self.field[x][y - 1].value:
                        return False
                    if self.field[x][y].value == self.field[x][y + 1].value:
                        return False
            for x in range(1, 3):
                for y in range(4):
                    if self.field[x][y].value == self.field[x - 1][y].value:
                        return False
                    if self.field[x][y].value == self.field[x + 1][y].value:
                        return False
        return True

    def spawn_random(self):
        empty = []
        for x in range(4):
            for y in range(4):
                if self.field[x][y] is None:
                    empty.append((x, y))
        x, y = random.choice(empty)
        self.field[x][y] = Tile(random.choice([1, 2]), (x, y))

    def any_moving(self):
        for x in range(*self.RANGES[self.direction[0]]):
            for y in range(*self.RANGES[self.direction[1]]):
                if self.field[x][y] is not None and self.field[x][y].direction != (
                    0,
                    0,
                ):
                    return True
        return False

    def _update_midgame(self, io, delta):
        # if not self.is_full():
        #    self.spawn_random()

        if io.controller.button_left.fresh_press():
            self.direction_queue.append((-1, 0))
        if io.controller.button_right.fresh_press():
            self.direction_queue.append((1, 0))
        if io.controller.button_up.fresh_press():
            self.direction_queue.append((0, -1))
        if io.controller.button_down.fresh_press():
            self.direction_queue.append((0, 1))

        moving = self.any_moving()
        if not moving and self.direction != (0, 0):
            self.direction = (0, 0)
            if not self.field_eq(self.field, self.last_field):
                self.spawn_random()
                self.last_field = self.copy_field(self.field)

        if not moving and len(self.direction_queue) > 0:
            self.direction = self.direction_queue[0]
            self.direction_queue = self.direction_queue[1:]
            for x in range(*self.RANGES[self.direction[0]]):
                for y in range(*self.RANGES[self.direction[1]]):
                    if self.field[x][y] is not None:
                        self.field[x][y].move(self.direction)

        for x in range(*self.RANGES[self.direction[0]]):
            for y in range(*self.RANGES[self.direction[1]]):
                if self.field[x][y] is not None:
                    self.score += self.field[x][y].update(self.field, delta)

        if self.is_game_over():
            self.score = round(math.log(self.score, 2))
            self.state = self.GAME_OVER

        io.display.fill((0, 0, 0))

        # Draw fields
        for x in range(4):
            for y in range(4):
                if self.field[x][y] is not None:
                    self.field[x][y].draw(io.display)

        score_bmp = textutils.get_text_bitmap(str(round(math.log(self.score, 2))))

        bitmaputils.apply_bitmap(
            score_bmp,
            io.display,
            (io.display.width // 2 - score_bmp.shape[1] // 2, 0),
            fg_color=(255, 255, 255),
        )

    def _update_gameover(self, io, delta):
        io.display.fill((0, 0, 0))

        for x in range(io.display.width):
            io.display.update(x, 5, RED)
            io.display.update(x, 14, RED)
        for y in range(5, io.display.height):
            io.display.update(0, y, RED)
            io.display.update(9, y, RED)
    
        # Draw fields
        for x in range(4):
            for y in range(4):
                if self.field[x][y] is not None:
                    self.field[x][y].draw(io.display)

        score_bmp = textutils.get_text_bitmap(str(round(math.log(self.score, 2))))

        bitmaputils.apply_bitmap(
            score_bmp,
            io.display,
            (io.display.width // 2 - score_bmp.shape[1] // 2, 0),
            fg_color=(255, 255, 255),
        )

        if io.controller.button_a.fresh_release():
            self.state = self.PRE_GAME