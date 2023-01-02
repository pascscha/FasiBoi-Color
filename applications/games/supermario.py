from applications.games import core
from helpers import textutils, bitmaputils, animations
import random
import cv2
import numpy as np


class MovingEntity:
    Y_DELTA = 0.1

    def __init__(self, parent, pos, size=(1, 1), fall=False, vel=(0, 0)):
        self.pos = pos
        self.parent = parent
        self.fall = fall
        self.vel = list(vel)
        self.size = size

    def is_colliding(self, x, y):
        for dx in range(self.size[0]):
            for dy in range(self.size[1]):
                if self.parent.is_solid(x + dx, y - dy):
                    return True
        return False

    def on_floor(self):
        for dx in range(self.size[0]):
            if self.parent.is_solid(self.pos[0] + dx, self.pos[1] + 1):
                return True
        return False

    def update(self, delta):
        if self.vel[1] > 0 and self.on_floor():
            self.vel[1] = 0
        else:
            self.vel[1] += self.parent.GRAVITY * delta

        new_x = self.pos[0] + self.vel[0] * delta
        new_y = self.pos[1] + self.vel[1] * delta

        if self.is_colliding(self.pos[0], new_y):
            self.vel[1] = 0
            new_y = self.pos[1]

        if self.is_colliding(new_x, new_y):
            self.vel[0] = 0
            new_x = self.pos[0]

        self.pos = [new_x, new_y]


class Goomba(MovingEntity):
    def __init__(self, *args, speed=2, **kwargs):
        super().__init__(*args, **kwargs)
        self.falling = not self.on_floor()
        self.speed = speed
        self.vel[0] = self.speed

    def update(self, delta):
        prev_pos = self.pos
        super().update(delta)
        if not self.falling and not self.on_floor():
            self.pos = prev_pos
            self.speed *= -1
            self.vel[0] = self.speed
            self.vel[1] = 0
        elif self.speed != 0 and self.vel[0] == 0:
            self.speed *= -1
            self.vel[0] = self.speed


class Supermario(core.Game):

    FLOOR_COLOR = (168, 0, 177)
    GOOMBA_COLOR = (0, 163, 0)
    BOX_COLOR = (255, 255, 0)
    MARIO_TROUSERS = (0, 0, 255)
    MARIO_HAT = (255, 0, 0)
    GRAVITY = 60
    SPEED = 7

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 0
        self.gameover_scroll = None
        self.gameover_bmp = textutils.get_text_bitmap("GAME OVER!")

    def load_level(self, level):
        level_data = cv2.imread(f"resources/images/supermario/{level}.png")
        self.floor_bmp = np.all(level_data == self.FLOOR_COLOR, axis=2)
        self.boxes = []

        self.goombas = [
            Goomba(self, (x, y))
            for y, x in zip(*np.where(np.all(level_data == self.GOOMBA_COLOR, axis=2)))
        ]
        # self.boxes = [
        #     (x - 1, y)
        #     for y, x in zip(
        #         *np.where(np.all(level_data == tuple(reversed(self.BOX_COLOR)), axis=2))
        #     )
        # ]
        self.mario_entity = MovingEntity(self, (4.5, 12.5), size=(1, 2))

    def reset(self, io):
        self.level = 0
        self.load_level(self.level)

    def is_box(self, x, y):
        ix = int(x)
        iy = int(y)
        return (ix, iy) in self.boxes

    def is_solid(self, x, y):
        ix = int(x)
        iy = int(y)
        if 0 <= ix < self.floor_bmp.shape[1] and 0 <= iy < self.floor_bmp.shape[0]:
            return self.floor_bmp[iy][ix] or self.is_box(x, y)
        else:
            return False

    def update_physics(self, delta):
        self.mario_entity.update(delta)

    def _update_midgame(self, io, delta):
        if io.controller.button_up.get_fresh_value():
            if self.is_solid(self.mario_entity.pos[0], self.mario_entity.pos[1] + 1):
                self.mario_entity.vel[1] = -0.4 * self.GRAVITY

        if io.controller.button_left.get_value():
            self.mario_entity.vel[0] = -self.SPEED
        elif io.controller.button_right.get_value():
            self.mario_entity.vel[0] = self.SPEED
        else:
            self.mario_entity.vel[0] = 0

        for goomba in self.goombas:
            goomba.update(delta)

        self.update_physics(delta)
        if self.mario_entity.pos[1] > io.display.height + 2:
            self.state = self.GAME_OVER

        kill = []
        for i, goomba in enumerate(self.goombas):
            if (
                abs(self.mario_entity.pos[0] - goomba.pos[0]) < 0.9
                and abs(self.mario_entity.pos[1] - goomba.pos[1]) < 1
            ):
                if self.mario_entity.vel[1] > 0.1:
                    kill.append(i)
                else:
                    self.mario_entity.vel[1] = -0.35 * self.GRAVITY
                    self.state = self.GAME_OVER
        for k in reversed(kill):
            self.goombas.pop(k)

        io.display.fill((0, 0, 0))
        self.draw_floor(io, delta)
        self.draw_goombas(io, delta)
        self.draw_boxes(io, delta)
        self.draw_mario(io, delta)

    def draw_goombas(self, io, delta):
        for goomba in self.goombas:
            ix = int(4.5 + goomba.pos[0] - self.mario_entity.pos[0])
            iy = int(goomba.pos[1])

            if 0 <= ix < io.display.width:
                if 0 <= iy < io.display.height:
                    io.display.update(ix, iy, self.GOOMBA_COLOR)

    def draw_boxes(self, io, delta):
        for x, y in self.boxes:
            ix = int(5 + x - self.mario_entity.pos[0])
            iy = int(y)

            if 0 <= ix < io.display.width:
                if 0 <= iy < io.display.height:
                    io.display.update(ix, iy, self.BOX_COLOR)

    def draw_mario(self, io, delta):
        iy = int(self.mario_entity.pos[1])

        if 0 <= iy < io.display.height:
            io.display.update(4, iy, self.MARIO_TROUSERS)
        if 1 <= iy < io.display.height + 1:
            io.display.update(4, iy - 1, self.MARIO_HAT)

    def draw_floor(self, io, delta):
        bitmaputils.apply_bitmap(
            self.floor_bmp,
            io.display,
            (4 - int(self.mario_entity.pos[0]), 0),
            fg_color=self.FLOOR_COLOR,
        )

    def _update_gameover(self, io, delta):
        if self.gameover_scroll is None:
            self.gameover_scroll = animations.AnimatedValue(0, speed=0.3)
            self.gameover_scroll.set_value(1)

        self.mario_entity.vel[0] = 0
        self.mario_entity.vel[1] += self.GRAVITY * delta
        self.mario_entity.pos[1] += self.mario_entity.vel[1] * delta

        io.display.fill((0, 0, 0))
        self.draw_floor(io, delta)
        self.draw_goombas(io, delta)
        self.draw_mario(io, delta)

        text_pos = self.gameover_scroll.tick(delta)
        x = int(
            (
                (1 - text_pos) * (io.display.width + self.gameover_bmp.shape[1])
                - self.gameover_bmp.shape[1]
            )
        )

        bitmaputils.apply_bitmap(
            self.gameover_bmp,
            io.display,
            (x, (io.display.height - self.gameover_bmp.shape[0]) // 2),
            fg_color=(255, 255, 255),
        )
        if text_pos == 1:
            self.gameover_scroll = None
            self.state = self.PRE_GAME
