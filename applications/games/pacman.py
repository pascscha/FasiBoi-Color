from applications.games import core
import random
import numpy as np


class Position:
    def __init__(self, x, y, width=10, height=15):
        self.width = width
        self.height = height
        self._x = x % width
        self._y = y % height

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, new_x):
        self._x = new_x % self.width

    @y.setter
    def y(self):
        return self.y % self.height

    def __add__(self, other):
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y, width=self.width, height=self.height)
        else:
            raise ValueError(f"Can't add {type(other)} to {type(self)}")

    def __sub__(self, other):
        if isinstance(other, Position):
            return Position(self.x - other.x, self.y - other.y, width=self.width, height=self.height)
        else:
            raise ValueError(f"Can't add {type(other)} to {type(self)}")

    def __mul__(self, other):
        if isinstance(other, int):
            return Position(self.x * other, self.y * other, width=self.width, height=self.height)
        else:
            raise ValueError(f"Can't add {type(other)} to {type(self)}")

    def __neg__(self):
        return Position(-self.x, -self.y, width=self.width, height=self.height)

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        else:
            return False

    def __repr__(self):
        return f"Position({self.x}, {self.y})"

    def squared_distance(self, other):
        return (self.x-other.x)**2 + (self.y-other.y)**2


class Field:
    EMPTY = 0
    WALL = 1
    FOOD = 2
    SUPER_FOOD = 3
    GHOST_DOOR = 4

    UP = Position(0, -1)
    DOWN = Position(0, 1)
    LEFT = Position(-1, 0)
    RIGHT = Position(1, 0)
    DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

    def __init__(self):
        self.field = np.load("resources/sprites/pacman.npy")
        self.base = [Position(4, 7), Position(5, 7)]
        self.base_entrance = Position(6, 5)

    def get_value(self, pos):
        return self.field[pos.x][pos.y]

    def set_value(self, pos, value):
        self.field[pos.x][pos.y] = value

    def draw(self, display, pulse_progression):
        prog1 = pulse_progression*2
        prog2 = pulse_progression
        bright1 = int(255 * (abs(prog1 - int(prog1) - 0.5)*0.5+0.5))
        bright2 = int(128 * (abs(prog2 - int(prog2) - 0.5)*0.5+0.5))

        display.fill((0, 0, 0))
        for x in range(display.width):
            for y in range(display.height):
                val = self.field[x][y]
                if val == self.WALL:
                    display.update(x, y, (0, 0, 255))
                elif val == self.GHOST_DOOR:
                    display.update(x, y, (128, 128, 255))
                elif val == self.FOOD:
                    display.update(x, y, (bright2, bright2, bright2))
                elif val == self.SUPER_FOOD:
                    display.update(x, y, (bright1, bright1, bright1))


class Entity:
    def __init__(self, field, pos, speed=5, color=(255, 255, 255), direction=Field.LEFT, obstacles=[Field.WALL, Field.GHOST_DOOR]):
        self.field = field
        self.pos = pos
        self.ticker = core.Ticker(speed)
        self.obstacles = obstacles
        self.direction = direction
        self.color = color
        self.age = 0

    def is_walkable(self, pos):
        return self.field.get_value(pos) not in self.obstacles

    def get_walkable_directions(self, backtrack=False):
        return [
            direction for direction in Field.DIRECTIONS
            if self.is_walkable(self.pos + direction)
            and (backtrack or direction != -self.direction)
        ]

    def update(self, delta):
        self.age += delta
        if self.ticker.tick(delta):
            self._update()

    def get_color(self):
        return self.color

    def draw(self, display):
        display.update(self.pos.x, self.pos.y, self.get_color())

    def _update(self):
        raise NotImplementedError("Please implement this method")


class Pac(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, color=(255, 255, 0), **kwargs)
        self.next_direction = None

    def change_direction(self, next_direction):
        self.next_direction = next_direction

    def _update(self):
        if self.next_direction is not None:
            new_pos = self.pos + self.next_direction
            if self.is_walkable(new_pos):
                self.direction = self.next_direction
                self.next_direction = None

        new_pos = self.pos + self.direction
        if self.is_walkable(new_pos):
            self.pos = new_pos


class Ghost(Entity):
    UNRELEASED = 0
    TARGET = 1
    FRIGHTENED = 2
    EATEN = 3

    def __init__(self, field, idle_target, *args, release=2, frighten_duration=5, release_after_eaten=2, target_speed=4, frightened_speed=3, eaten_speed=6, **kwargs):
        super().__init__(field, random.choice(field.base),
                         *args, speed=target_speed, **kwargs)
        self.state = self.UNRELEASED
        self.pos = random.choice(self.field.base)
        self.idle_target = idle_target
        self.target = idle_target

        self.target_speed = target_speed
        self.frightened_speed = frightened_speed
        self.eaten_speed = eaten_speed

        self.release = release
        self.frighten_time = 0
        self.frighten_duration = frighten_duration
        self.release_after_eaten = release_after_eaten

    def _update(self):
        # Update state
        if self.state == self.UNRELEASED:
            if self.age > self.release:
                self.pos = self.field.base_entrance
                self.state = self.TARGET
        elif self.state == self.FRIGHTENED:
            if self.age - self.frighten_time > self.frighten_duration:
                self.state = self.TARGET
        elif self.state == self.EATEN:
            if self.pos == self.field.base_entrance:
                self.state = self.UNRELEASED
                self.release = self.age + self.release_after_eaten

        # Move according to state
        if self.state == self.UNRELEASED:
            self.update_unreleased()
        elif self.state == self.TARGET:
            self.ticker.speed = self.frightened_speed
            self.update_target()
        elif self.state == self.FRIGHTENED:
            self.ticker.speed = self.frightened_speed
            self.update_frightened()
        elif self.state == self.EATEN:
            self.ticker.speed = self.eaten_speed
            self.update_eaten()

    def frighten(self):
        if self.state == self.TARGET:
            self.state = self.FRIGHTENED
            self.frighten_time = self.age

    def go_to(self, target):
        directions = self.get_walkable_directions()
        return min(
            directions,
            key=lambda d: target.squared_distance(self.pos + d)
        )

    def update_unreleased(self):
        self.pos = random.choice(self.field.base)

    def update_target(self):
        self.direction = self.go_to(self.target)
        self.pos += self.direction

    def update_frightened(self):
        self.direction = random.choice(self.get_walkable_directions())
        self.pos += self.direction

    def update_eaten(self):
        self.direction = self.go_to(self.field.base_entrance)
        print(self.field.base_entrance, self.pos)
        self.pos += self.direction

    def get_color(self):
        if self.state == self.FRIGHTENED:
            return (64, 64, 255)
        elif self.state == self.EATEN:
            return (200, 200, 200)
        else:
            return self.color


class Pacman(core.Game):
    SPREAD = 1
    ATTACK = 0

    def reset(self, io):
        self.field = Field()
        self.pac = Pac(self.field, Position(4, 11),
                       speed=5, direction=Field.RIGHT)
        self.score = 0

        self.blinky = Ghost(self.field, Position(9, 0),
                            color=(255, 0, 38))
        self.pinky = Ghost(self.field, Position(
            0, 0), color=(255, 182, 251))
        self.inky = Ghost(self.field, Position(9, 14),
                          color=(0, 255, 253))
        self.clyde = Ghost(self.field, Position(
            0, 14), color=(255, 181, 97))
        self.ghosts = [self.clyde, self.inky, self.pinky, self.blinky]
        self.level_age = 0

        self.attacks = [20, 40, 60]
        self.defenses = [30, 50]
        self.mode = self.SPREAD

    def _update_midgame(self, io, delta):
        self.level_age += delta
        if io.controller.left.get_fresh_value():
            self.pac.change_direction(Field.LEFT)
        if io.controller.right.get_fresh_value():
            self.pac.change_direction(Field.RIGHT)
        if io.controller.up.get_fresh_value():
            self.pac.change_direction(Field.UP)
        if io.controller.down.get_fresh_value():
            self.pac.change_direction(Field.DOWN)

        if self.mode == self.SPREAD:
            if len(self.attacks) > 0 and self.level_age > self.attacks[0]:
                print("attack")
                self.mode = self.ATTACK
                self.attacks = self.attacks[1:]
                for ghost in self.ghosts:
                    ghost.direction = -ghost.direction
            else:
                for ghost in self.ghosts:
                    ghost.target = ghost.idle_target

        elif self.mode == self.ATTACK:
            if len(self.defenses) > 0 and self.level_age > self.defenses[0]:
                self.mode = self.SPREAD
                print("spread")
                self.defenses = self.defenses[1:]
            else:
                self.blinky.target = self.pac.pos
                self.pinky.target = self.pac.pos + self.pac.direction * 2
                self.inky.target = self.pac.pos * 2 - self.blinky.pos
                if self.clyde.pos.squared_distance(self.pac.pos) > 4:
                    self.clyde.target = self.clyde.idle_target
                else:
                    self.clyde.target = self.pac.pos

        self.pac.update(delta)

        if self.field.get_value(self.pac.pos) == Field.FOOD:
            self.field.set_value(self.pac.pos, Field.EMPTY)
            self.score += 1
        elif self.field.get_value(self.pac.pos) == Field.SUPER_FOOD:
            self.field.set_value(self.pac.pos, Field.EMPTY)
            self.score += 5
            for ghost in self.ghosts:
                ghost.frighten()

        for ghost in self.ghosts:
            if self.pac.pos == ghost.pos:
                if ghost.state == ghost.FRIGHTENED:
                    ghost.state = ghost.EATEN
                    self.score += 10
                elif ghost.state == ghost.TARGET:
                    self.state = self.GAME_OVER
                    return
            ghost.update(delta)

        self.field.draw(io.display, self.pulse_progression)
        for ghost in self.ghosts:
            ghost.draw(io.display)
        self.pac.draw(io.display)
