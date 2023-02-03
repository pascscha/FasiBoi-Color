from applications.colors import *
from applications.games import core
from helpers import animations, bitmaputils
import random
import cv2
import os
import time

class Racer(core.Game):
    RESOURCES_PATH = "resources/images/racer"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.car_sprite = self.load_sprite("car.png", alpha=True)
        self.obstacle_sprites = [
            self.load_sprite("obstacle_car.png", alpha=True),
            self.load_sprite("obstacle_dog.png", alpha=True),
            self.load_sprite("obstacle_hole.png", alpha=True),
            self.load_sprite("obstacle_sign.png", alpha=True),
            self.load_sprite("obstacle_tree.png", alpha=True)
        ]

    def load_sprite(self, name, alpha=False):
        if alpha:
            return cv2.cvtColor(cv2.imread(os.path.join(self.RESOURCES_PATH, name), cv2.IMREAD_UNCHANGED), cv2.COLOR_RGB2BGR)
        else:
            return cv2.cvtColor(cv2.imread(os.path.join(self.RESOURCES_PATH, name)), cv2.COLOR_RGB2BGR)
    
    def reset(self, io):
        self.score = 0

        self.distance = 0
        self.animated_distance = animations.AnimatedValue(self.distance, speed=3)
        self.lane = 0
        self.animated_lane = animations.AnimatedValue(self.lane, speed=3)

        self.fuel = 1        
        self.fuel_speed = 0.2
        self.fuel_add = 0.1

        self.obstacle_distance = 3
        self.obstacles = []
        for o in range(4):
            self.obstacles.append((10 + o * 5 * int(self.obstacle_distance), random.choice(self.obstacle_sprites), random.choice([0,1])))

        self.fresh_gameover = True
    
    def draw(self, io, delta):
        io.display.fill((0,0,0))
        d = self.animated_distance.tick(delta)
        l = self.animated_lane.tick(delta)

        lane_x = int(io.display.width//2 - 2 + 3 * (1 - l))

        for y in range(io.display.height):
            if int((y - d)/3)%2 == 0:
                io.display.update(lane_x, y, (64, 64, 0))

        while (d - self.obstacles[0][0]) > io.display.height:
            self.obstacles = self.obstacles[1:]
            self.obstacles.append((self.obstacles[-1][0] + 5 * int(self.obstacle_distance), random.choice(self.obstacle_sprites), random.choice([0,1])))
            self.obstacle_distance = max(self.obstacle_distance - 0.1, 1)
            self.fuel_add *= 0.95
            self.score += 1

        for (distance, sprite, lane) in self.obstacles:                
            bitmaputils.apply_image(sprite, io.display, (lane_x - 6 + lane*8, int(d - distance)))

        bitmaputils.apply_image(self.car_sprite, io.display, (int(l*(io.display.width-5)), io.display.height-5))
            

        if self.fuel < 0.5:
            fuel_color = animations.blend_colors(RED, YELLOW * 0.5, self.fuel * 2)
        else:
            fuel_color = animations.blend_colors(YELLOW * 0.5, GREEN * 0.5, (self.fuel - 0.5)* 2)
        
        for x in range(1 + round((io.display.width-1) * self.fuel)):
            io.display.update(x, 0, fuel_color)
        
    def _update_midgame(self, io, delta):        
        moved = False
        if io.controller.button_up.fresh_press():
            self.distance += 5
            moved = True

        if io.controller.button_left.fresh_press():
            self.distance += 5
            self.lane = 0
            moved = True

        if io.controller.button_right.fresh_press():
            self.distance += 5
            self.lane = 1
            moved = True

        if moved:
            for obstacle in self.obstacles:
                if self.distance-10 == obstacle[0] and self.lane == obstacle[2]:
                    self.state = self.GAME_OVER
                self.animated_distance.set_value(self.distance)
                self.animated_lane.set_value(self.lane)
                self.fuel = min(1, self.fuel + self.fuel_add)

        self.fuel -= self.fuel_speed * delta

        self.draw(io, delta)

        if self.fuel < 0:
            self.state = self.GAME_OVER
    
    def _update_gameover(self, io, delta):
        if self.fresh_gameover:
            self.fresh_gameover = False
            if self.fuel > 0:
                self.distance -= 3
                self.animated_distance.set_value(self.distance)
                self.animated_distance.speed = 5
            else:
                self.animated_distance.speed = 0.5

        self.draw(io, delta)

        if io.controller.button_a.fresh_release():
            self.state = self.PRE_GAME
