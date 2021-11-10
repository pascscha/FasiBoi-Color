from applications.games import core
from helpers import bitmaputils
import random
import cv2
import numpy as np

class Supermario(core.Game):

    FLOOR_COLOR = (168, 0, 177)
    GOOMBA_COLOR = (0, 163, 0)
    MARIO_TROUSERS = (0, 0, 255)
    MARIO_HAT = (255, 0, 0)
    GRAVITY = 15
    SPEED = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 0

    def load_level(self, level):
        level_data = cv2.imread(f"resources/images/supermario/{level}.png") 
        self.floor_bmp = np.all(level_data == self.FLOOR_COLOR, axis=2)
        self.goombas = list(zip(*np.where(np.all(level_data == self.GOOMBA_COLOR, axis=2))))
        
    def reset(self, io):
        self.level = 0
        self.load_level(self.level)
        self.mario_pos = [4.5, 12.5]
        self.mario_vel = [0, 0]

    def is_solid(self, x, y):
        ix = int(x)
        iy = int(y)
        if 0 <= ix < self.floor_bmp.shape[1] and 0 <= iy < self.floor_bmp.shape[0]:
            return self.floor_bmp[iy][ix]
        else:
            return False

    def update_physics(self, delta):
        on_floor = self.is_solid(self.mario_pos[0], self.mario_pos[1]+1)

        if self.mario_vel[1] > 0 and on_floor:
            self.mario_vel[1] = 0

        if not self.is_solid(self.mario_pos[0] + self.mario_vel[0] * delta, self.mario_pos[1]) and \
                not self.is_solid(self.mario_pos[0] + self.mario_vel[0] * delta, self.mario_pos[1] -1):
            self.mario_pos[0] += self.mario_vel[0] * delta


        if not self.is_solid(self.mario_pos[0], self.mario_pos[1] + self.mario_vel[1] * delta) and \
                not self.is_solid(self.mario_pos[0], self.mario_pos[1] + self.mario_vel[1] * delta - 1):
            self.mario_pos[1] += self.mario_vel[1] * delta
        else:
            self.mario_vel[1] = 0
        if not on_floor:
            self.mario_vel[1] += self.GRAVITY * delta

    def _update_midgame(self, io, delta):
        if io.controller.button_up.get_fresh_value():
            if self.is_solid(self.mario_pos[0], self.mario_pos[1]+1):
                self.mario_vel[1] = -0.7*self.GRAVITY

        if io.controller.button_left.get_value():
            self.mario_vel[0] = -self.SPEED
        elif io.controller.button_right.get_value():
            self.mario_vel[0] = self.SPEED
        else:
            self.mario_vel[0] = 0

        self.update_physics(delta)
        if self.mario_pos[1] > io.display.height + 2:
            self.state = self.GAME_OVER

        kill = []
        for i,goomba in enumerate(self.goombas):
            if abs(self.mario_pos[0] - goomba[0]) < 1 and abs(self.mario_pos[1] - goomba[1] + 1) < 1:
                if self.mario_vel[1] > 0:
                    kill.append(i)
                else:
                    self.state = self.GAME_OVER

        for k in reversed(kill):
            self.goombas.pop(k)

        io.display.fill((0, 0, 0))
        self.draw_floor(io, delta)
        self.draw_goombas(io, delta)
        self.draw_mario(io, delta)

    def draw_goombas(self, io, delta):
        for goomba in self.goombas:
            ix = int(4 + goomba[0] - self.mario_pos[0])
            iy = int(goomba[1]-1)

            if 0 <= ix < io.display.width:
                if 0 <= iy < io.display.height:
                    io.display.update(ix, iy, self.GOOMBA_COLOR)
        

    def draw_mario(self, io, delta):
        iy = int(self.mario_pos[1])

        if 0 <= iy < io.display.height:
            io.display.update(4, iy, self.MARIO_TROUSERS)
        if 1 <= iy < io.display.height + 1:
            io.display.update(4, iy-1, self.MARIO_HAT)

    def draw_floor(self, io, delta):
        bitmaputils.apply_bitmap(self.floor_bmp, io.display, (4-int(self.mario_pos[0]), 0), fg_color=self.FLOOR_COLOR)
 
    #def _update_gameover(self, io, delta):
    #    pass
