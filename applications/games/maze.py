from applications.games import core
from applications.games.alphabeta import BitField
from helpers import animations
from IO.color import *
import random
import time


def printbb(maze, bb):
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.get_bitmask(x, y) & bb:
                print("x", end=" ")
            else:
                print(".", end=" ")
        print()
    print()


class MazeUtils:
    INFINITY = 0xDEADBEEF

    @classmethod
    def get_deletable_walls(cls, maze):
        free = maze.bits1
        walls = ~free
        free1 = walls & free << 1
        free2 = walls & free << maze.width
        free3 = walls & free >> 1
        free4 = walls & free >> maze.width

        one_free_neighbour = (
            free1 & ~free2 & ~free3 & ~free4
            | ~free1 & free2 & ~free3 & ~free4
            | ~free1 & ~free2 & free3 & ~free4
            | ~free1 & ~free2 & ~free3 & free4
        )

        for x in range(1, maze.width - 1):
            for y in range(1, maze.height - 1):
                if one_free_neighbour & maze.get_bitmask(x, y):
                    yield ((x, y))

    @classmethod
    def bfs(cls, maze, start):
        distances = [
            [cls.INFINITY for _ in range(maze.height)] for _ in range(maze.height)
        ]
        distances[start[0]][start[1]] = 0
        queue = [(start, 0)]
        while len(queue) > 0:
            loc, d = queue[0]
            x, y = loc
            queue = queue[1:]
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx = x + dx
                ny = y + dy
                if (
                    0 <= nx < maze.width
                    and 0 <= ny < maze.height
                    and maze.get_value(nx, ny) == BitField.COLOR1
                ):
                    if distances[nx][ny] == cls.INFINITY:
                        distances[nx][ny] = d + 1
                        queue.append(((nx, ny), d + 1))
        return distances

    @classmethod
    def generate_maze(cls, width, height):
        maze = BitField(width, height)
        maze.set_value(width // 2, 0, BitField.COLOR1)
        maze.set_value(width // 2, height - 1, BitField.COLOR1)
        deletable = list(cls.get_deletable_walls(maze))
        while len(deletable) > 0:
            x, y = random.choice(deletable)
            maze.set_value(x, y, BitField.COLOR1)
            deletable = list(cls.get_deletable_walls(maze))

        distances1 = cls.bfs(maze, (width // 2, 0))
        distances2 = cls.bfs(maze, (width // 2, height - 1))

        best_distance = None
        best_pos = None
        for x in range(1, maze.width - 1):
            for y in range(1, maze.height - 1):
                if maze.get_value(x, y) != BitField.COLOR1:
                    d1_1 = distances1[x - 1][y]
                    d1_2 = distances1[x + 1][y]
                    d1_3 = distances1[x][y - 1]
                    d1_4 = distances1[x][y + 1]
                    d2_1 = distances2[x - 1][y]
                    d2_2 = distances2[x + 1][y]
                    d2_3 = distances2[x][y - 1]
                    d2_4 = distances2[x][y + 1]

                    n1 = sum(map(lambda x: x != cls.INFINITY, [d1_1, d1_2, d1_3, d1_4]))
                    n2 = sum(map(lambda x: x != cls.INFINITY, [d2_1, d2_2, d2_3, d2_4]))
                    d1 = min([d1_1, d1_2, d1_3, d1_4])
                    d2 = min([d2_1, d2_2, d2_3, d2_4])

                    if (
                        n1 == 1
                        and n2 == 1
                        and (best_distance is None or d1 + d2 > best_distance)
                    ):
                        best_distance = d1 + d2
                        best_pos = (x, y)

        if best_pos is None:
            return cls.generate_maze(width, height)
        else:
            maze.set_value(*best_pos, BitField.COLOR1)

        return maze, (distances1, distances2)


class Maze(core.Game):
    MISERE = True
    DEFAULT_SCORE = 99
    MOVE_SPEED = 0.2

    def reset(self, io):
        self.maze, _ = MazeUtils.generate_maze(io.display.width, io.display.height)
        self.pos = (self.maze.width // 2, 0)
        self.score = 0
        self.last_moved = time.time()

    def _update_midgame(self, io, delta):
        new_pos = self.pos
        self.score += delta

        if io.controller.button_b.fresh_press():
            self.reset(io)
            return

        now = time.time()
        time_since_last_moved = time.time() - self.last_moved

        if (
            io.controller.button_left.fresh_press()
            or io.controller.button_left.get_value()
            and time_since_last_moved >= self.MOVE_SPEED
        ):
            self.last_moved = now
            new_pos = (self.pos[0] - 1, self.pos[1])
        if (
            io.controller.button_right.fresh_press()
            or io.controller.button_right.get_value()
            and time_since_last_moved >= self.MOVE_SPEED
        ):
            self.last_moved = now
            new_pos = (self.pos[0] + 1, self.pos[1])
        if (
            io.controller.button_up.fresh_press()
            or io.controller.button_up.get_value()
            and time_since_last_moved >= self.MOVE_SPEED
        ):
            self.last_moved = now
            new_pos = (self.pos[0], self.pos[1] - 1)
        if (
            io.controller.button_down.fresh_press()
            or io.controller.button_down.get_value()
            and time_since_last_moved >= self.MOVE_SPEED
        ):
            self.last_moved = now
            new_pos = (self.pos[0], self.pos[1] + 1)

        if (
            0 <= new_pos[0] < self.maze.width
            and 0 <= new_pos[1] < self.maze.height
            and self.maze.get_value(*new_pos) == BitField.COLOR1
        ):
            self.pos = new_pos
            if self.pos[1] == self.maze.height - 1:
                self.state = self.GAME_OVER

        io.display.fill((0, 0, 0))
        for x in range(io.display.width):
            for y in range(io.display.height):
                if self.maze.get_value(x, y) == BitField.EMPTY:
                    io.display.update(x, y, (0, 128, 0))

        io.display.update(*self.pos, RED)


if __name__ == "__main__":
    Maze.generate_maze(10, 15)
