from applications.games import core
from helpers import textutils, bitmaputils, animations
import random
import cv2
import numpy as np


# class MovingEntity:
#     Y_DELTA=0.1

#     def __init__(self, pos, parent, size=(1,1), fall=False, vel=(2, 0)):
#         self.pos = pos
#         self.parent = parent
#         self.fall = fall
#         self.vel = list(vel)
#         self.size = size

#     def is_colliding(self, x, y):
#         for dx in range(self.size[0]):
#             for dy in range(self.size[1]):
#                 if self.parent.is_solid(x + dy, y+dy):
#                     return True
#         return False

#     def update_physics(self, delta):
#         # on_floor = self.parent.is_solid(self.pos[0], self.pos[1] + 1)
#         # if self.velocity[1] > 0 and on_floor:
#         #     self.velocity[1] = 0
#         self.vel[1] += self.parent.GRAVITY * delta

#         new_x = self.pos[0] + self.vel[0] * delta
#         new_y = self.pos[1] + self.vel[1] * delta
        
#         if self.is_colliding(new_x, pos[1]):
#             self.vel[0] = 0
#             self.new_x = pos[0]
        
#         if self.is_colliding(new_x, new_y):
#             self.vel[1] = 0
#             self.new_y = pos[1]
        

        # if not self.is_solid(
        #     self.mario_pos[0] + self.mario_vel[0] * delta, self.mario_pos[1]
        # ) and not self.is_solid(
        #     self.mario_pos[0] + self.mario_vel[0] * delta, self.mario_pos[1] - 1
        # ):
        #     self.mario_pos[0] += self.mario_vel[0] * delta

        # if not self.is_solid(
        #     self.mario_pos[0], self.mario_pos[1] + self.mario_vel[1] * delta
        # ) and not self.is_solid(
        #     self.mario_pos[0], self.mario_pos[1] + self.mario_vel[1] * delta - 1
        # ):
        #     self.mario_pos[1] += self.mario_vel[1] * delta
        # else:
        #     ix = int(self.mario_pos[0])
        #     iy = int(self.mario_pos[1] + self.mario_vel[1] * delta - 1)
        #     if self.is_box(ix, iy):
        #         self.boxes.remove((ix, iy))
        #     self.mario_vel[1] = 0

        # if not on_floor:
        #     self.mario_vel[1] += self.GRAVITY * delta


class MovingEntity:
    def __init__(self, pos, parent, fall=False, velocity=(2, 0)):
        self.pos = pos
        self.parent = parent
        self.fall = fall
        self.velocity = list(velocity)

    def update(self, delta):
        new_x = self.pos[0] + self.velocity[0] * delta

        new_y = self.pos[1]

        if (
            self.fall or self.parent.is_solid(new_x - 0.5, new_y + 1.5)
        ) and not self.parent.is_solid(new_x - 0.5, new_y + 0.5):

            if self.fall and not self.parent.is_solid(new_x - 0.5, new_y + 1.5):
                self.velocity[1] += self.parent.GRAVITY * delta
                new_y = self.pos[1] + self.velocity[1] * delta
            else:
                new_y = int(new_y)
            self.pos = (new_x, new_y)
        else:
            self.velocity[0] *= -1


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
        self.goombas = [
            MovingEntity((x, y), self)
            for y, x in zip(*np.where(np.all(level_data == self.GOOMBA_COLOR, axis=2)))
        ]
        self.boxes = [
            (x - 1, y)
            for y, x in zip(
                *np.where(np.all(level_data == tuple(reversed(self.BOX_COLOR)), axis=2))
            )
        ]
        print(self.boxes)
        print(level_data)

    def reset(self, io):
        self.level = 0
        self.load_level(self.level)
        self.mario_pos = [4.5, 12.5]
        self.mario_vel = [0, 0]

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
        on_floor = self.is_solid(self.mario_pos[0], self.mario_pos[1] + 1)

        if self.mario_vel[1] > 0 and on_floor:
            self.mario_vel[1] = 0

        if not self.is_solid(
            self.mario_pos[0] + self.mario_vel[0] * delta, self.mario_pos[1]
        ) and not self.is_solid(
            self.mario_pos[0] + self.mario_vel[0] * delta, self.mario_pos[1] - 1
        ):
            self.mario_pos[0] += self.mario_vel[0] * delta

        if not self.is_solid(
            self.mario_pos[0], self.mario_pos[1] + self.mario_vel[1] * delta
        ) and not self.is_solid(
            self.mario_pos[0], self.mario_pos[1] + self.mario_vel[1] * delta - 1
        ):
            self.mario_pos[1] += self.mario_vel[1] * delta
        else:
            ix = int(self.mario_pos[0])
            iy = int(self.mario_pos[1] + self.mario_vel[1] * delta - 1)
            if self.is_box(ix, iy):
                self.boxes.remove((ix, iy))
            self.mario_vel[1] = 0

        if not on_floor:
            self.mario_vel[1] += self.GRAVITY * delta

    def _update_midgame(self, io, delta):
        if io.controller.button_up.get_fresh_value():
            if self.is_solid(self.mario_pos[0], self.mario_pos[1] + 1):
                self.mario_vel[1] = -0.35 * self.GRAVITY

        if io.controller.button_left.get_value():
            self.mario_vel[0] = -self.SPEED
        elif io.controller.button_right.get_value():
            self.mario_vel[0] = self.SPEED
        else:
            self.mario_vel[0] = 0

        for goomba in self.goombas:
            goomba.update(delta)

        self.update_physics(delta)
        if self.mario_pos[1] > io.display.height + 2:
            self.state = self.GAME_OVER

        kill = []
        for i, goomba in enumerate(self.goombas):
            if (
                abs(self.mario_pos[0] - goomba.pos[0]) < 0.9
                and abs(self.mario_pos[1] - goomba.pos[1]) < 1
            ):
                if self.mario_vel[1] > 0:
                    kill.append(i)
                else:
                    self.mario_vel[1] = -0.35 * self.GRAVITY
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
            ix = int(4 + goomba.pos[0] - self.mario_pos[0])
            iy = int(goomba.pos[1])

            if 0 <= ix < io.display.width:
                if 0 <= iy < io.display.height:
                    io.display.update(ix, iy, self.GOOMBA_COLOR)

    def draw_boxes(self, io, delta):
        for x, y in self.boxes:
            ix = int(5 + x - self.mario_pos[0])
            iy = int(y)

            if 0 <= ix < io.display.width:
                if 0 <= iy < io.display.height:
                    io.display.update(ix, iy, self.BOX_COLOR)

    def draw_mario(self, io, delta):
        iy = int(self.mario_pos[1])

        if 0 <= iy < io.display.height:
            io.display.update(4, iy, self.MARIO_TROUSERS)
        if 1 <= iy < io.display.height + 1:
            io.display.update(4, iy - 1, self.MARIO_HAT)

    def draw_floor(self, io, delta):
        bitmaputils.apply_bitmap(
            self.floor_bmp,
            io.display,
            (4 - int(self.mario_pos[0]), 0),
            fg_color=self.FLOOR_COLOR,
        )

    def _update_gameover(self, io, delta):
        if self.gameover_scroll is None:
            self.gameover_scroll = animations.AnimatedValue(0, speed=0.3)
            self.gameover_scroll.set_value(1)

        self.mario_vel[0] = 0
        self.mario_vel[1] += self.GRAVITY * delta
        self.mario_pos[1] += self.mario_vel[1] * delta

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
