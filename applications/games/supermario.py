from applications.games import core
from helpers import textutils, bitmaputils, animations
import random
import cv2
import numpy as np
from IO.color import *
import random


class Collision:
    def __init__(self, vertical, velocity, other):
        self.vertical = vertical
        self.velocity = velocity
        self.other = other


class MovingEntity:
    Y_DELTA = 0.1

    def __init__(
        self,
        parent,
        pos,
        size=(1, 1),
        fall=True,
        vel=(0, 0),
        horiz_bounce=False,
        collide_box=True,
        collide_entity=False,
        collide_floor=True,
    ):
        self.pos = pos
        self.parent = parent
        self.fall = fall
        self.vel = list(vel)
        self.size = size
        self.horiz_bounce = horiz_bounce
        self.collide_box = collide_box
        self.collide_entity = collide_entity
        self.collide_floor = collide_floor

    def is_colliding(self, x, y):
        for dx in range(self.size[0]):
            for dy in range(self.size[1]):
                collision = self.parent.get_collision(
                    x + dx,
                    y - dy,
                    box=self.collide_box,
                    entity=self.collide_entity,
                    floor=self.collide_floor,
                )
                if collision is not None:
                    return collision
        return None

    def on_floor(self):
        for dx in range(self.size[0]):
            col = self.parent.get_collision(self.pos[0] + dx, self.pos[1] + 1)
            if col is not None:
                return col
        return None

    def update(self, delta):
        collisions = []

        col0 = self.on_floor()
        if col0 is not None:
            collisions.append(Collision(True, self.vel[1], col0))

        if self.vel[1] > 0 and col0 is not None:
            self.vel[1] = 0
        elif self.fall:
            self.vel[1] += self.parent.GRAVITY * delta

        new_x = self.pos[0] + self.vel[0] * delta
        new_y = self.pos[1] + self.vel[1] * delta

        col1 = self.is_colliding(self.pos[0], new_y)
        if col1 is not None:
            collisions.append(Collision(True, self.vel[1], col1))
            self.vel[1] = 0
            new_y = self.pos[1]

        col2 = self.is_colliding(new_x, new_y)
        if col2 is not None:
            collisions.append(Collision(False, self.vel[0], col2))
            if self.horiz_bounce:
                self.vel[0] *= -1
            else:
                self.vel[0] = 0

            new_x = self.pos[0]

        self.pos = [new_x, new_y]
        return collisions


class Goomba(MovingEntity):
    def __init__(self, *args, speed=2, **kwargs):
        super().__init__(
            *args,
            collide_entity=False,
            collide_floor=True,
            horiz_bounce=True,
            size=(1, 1),
            **kwargs,
        )
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


class Powerup(MovingEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, horiz_bounce=True, **kwargs)
        self.hue_animation = animations.Ticker(speed=1)

    def update(self, delta):
        super().update(delta)
        self.hue_animation.tick(delta)


class Supermario(core.Game):

    FLOOR_COLOR = (168, 0, 177)
    GOOMBA_COLOR = (0, 163, 0)
    BOX_COLOR = (255, 255, 0)
    MARIO_TROUSERS = (0, 0, 255)
    MARIO_HAT = (255, 0, 0)
    GRAVITY = 60
    SPEED = 7
    SUPER_TIME = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 0
        self.gameover_scroll = None
        self.gameover_bmp = textutils.get_text_bitmap("GAME OVER!")

    def load_level(self, level):
        level_data = cv2.imread(f"resources/images/supermario/{level}.png")
        self.floor_bmp = np.all(level_data == self.FLOOR_COLOR, axis=2)
        self.boxes = []
        self.entities = []
        self.goombas = []
        self.dead_goombas = []
        self.powerups = []

        self.goombas = [
            Goomba(self, (x, y))
            for y, x in zip(*np.where(np.all(level_data == self.GOOMBA_COLOR, axis=2)))
        ]

        self.entities += self.goombas

        self.boxes = [
            (x, y)
            for y, x in zip(
                *np.where(np.all(level_data == tuple(reversed(self.BOX_COLOR)), axis=2))
            )
        ]

        self.mario_entity = MovingEntity(
            self, (4.5, 12.5), size=(1, 2), collide_entity=True
        )

        self.super = False
        self.super_time = 0
        self.super_hue_animation = animations.Ticker(speed=1)

    def reset(self, io):
        self.score = 0
        self.level = 0
        self.load_level(self.level)

    def get_box(self, x, y):
        ix = int(x)
        iy = int(y)
        if (ix, iy) in self.boxes:
            return (ix, iy)
        return None

    def get_entity(self, x, y):
        for entity in self.entities:
            if abs(x - entity.pos[0]) < 1 and abs(y - entity.pos[1]) < 1:
                return entity
        return None

    def get_collision(self, x, y, box=True, entity=True, floor=True):
        ix = int(x)
        iy = int(y)
        if 0 <= ix < self.floor_bmp.shape[1] and 0 <= iy < self.floor_bmp.shape[0]:
            if floor and self.floor_bmp[iy][ix]:
                return True
            if box:
                b = self.get_box(x, y)
                if b is not None:
                    return b
            if entity:
                e = self.get_entity(x, y)
                if e is not None:
                    return e
        else:
            return None

    def update_physics(self, delta):
        collisions = self.mario_entity.update(delta)
        for col in collisions:
            if col.other in self.boxes:
                if col.vertical and col.velocity < 0:
                    self.boxes.remove(col.other)
                    x, y = col.other
                    p = Powerup(self, (x + 0.5, y), vel=(random.randint(-7, 7), -15))
                    self.entities.append(p)
                    self.powerups.append(p)

            if col.other in self.goombas:
                if self.super or col.vertical and col.velocity > 0:
                    self.goombas.remove(col.other)
                    self.entities.remove(col.other)
                    self.dead_goombas.append(col.other)
                    col.other.collide_floor = False
                    self.score += 1
                else:
                    self.state = self.GAME_OVER
                    self.mario_entity.vel[1] = -0.3 * self.GRAVITY

            if col.other in self.powerups:
                self.powerups.remove(col.other)
                self.score += 5
                self.super = True
                self.super_time = self.SUPER_TIME

    def _update_midgame(self, io, delta):
        if (
            io.controller.button_up.get_fresh_value()
            or io.controller.button_a.get_fresh_value()
        ):
            if self.get_collision(
                self.mario_entity.pos[0], self.mario_entity.pos[1] + 1
            ):
                self.mario_entity.vel[1] = -0.4 * self.GRAVITY

        if io.controller.button_left.get_value():
            if self.super:
                self.mario_entity.vel[0] = -1.5 * self.SPEED
            else:
                self.mario_entity.vel[0] = -self.SPEED
        elif io.controller.button_right.get_value():
            if self.super:
                self.mario_entity.vel[0] = 1.5 * self.SPEED
            else:
                self.mario_entity.vel[0] = self.SPEED
        else:
            self.mario_entity.vel[0] = 0

        for entity in self.entities:
            entity.update(delta)

        self.update_physics(delta)

        if self.mario_entity.pos[1] > io.display.height + 2:
            self.state = self.GAME_OVER

        if self.super:
            self.super_hue_animation.tick(delta)
            self.super_time -= delta
            if self.super_time < 0:
                self.super = False

        io.display.fill((0, 0, 0))
        self.draw_floor(io, delta)
        self.draw_goombas(io, delta)
        self.draw_powerups(io, delta)
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

    def draw_powerups(self, io, delta):
        for powerup in self.powerups:
            ix = int(4.5 + powerup.pos[0] - self.mario_entity.pos[0])
            iy = int(powerup.pos[1])
            if 0 <= ix < io.display.width:
                if 0 <= iy < io.display.height:
                    color = Color.from_hsv(powerup.hue_animation.progression, 1, 1)
                    io.display.update(ix, iy, color)

    def draw_mario(self, io, delta):
        iy = int(self.mario_entity.pos[1])
        if self.super:
            super_color = Color.from_hsv(self.super_hue_animation.progression, 1, 1)

        if 0 <= iy < io.display.height:
            if self.super:
                io.display.update(4, iy, super_color)
            else:
                io.display.update(4, iy, self.MARIO_TROUSERS)

        if 1 <= iy < io.display.height + 1:
            if self.super:
                io.display.update(4, iy - 1, super_color)
            else:
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

        for entity in self.entities:
            entity.update(delta)

        io.display.fill((0, 0, 0))
        self.draw_floor(io, delta)
        self.draw_goombas(io, delta)
        self.draw_powerups(io, delta)
        self.draw_boxes(io, delta)
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
