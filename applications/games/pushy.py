from IO.color import Color, BLACK, GREEN
from applications.games import core
from helpers import animations
import random
import numpy as np
import json
import os
from pprint import pprint
from applications.menu import Choice, SlidingChoice


class PushyState:
    EMPTY = 0
    PUSHY = 1
    WALL = 2
    BOX = 3
    HOME = 4
    PORTAL = 5
    BALL = 6
    GOAL = 7

    def __init__(self, shape, pos=(0, 0)):
        self.width, self.height = shape
        self.field = np.ones(shape, dtype=np.uint8) * self.EMPTY
        self.pos = pos
        self.portals = None

    def set(self, x, y, value):
        self.field[x, y] = value
        self.portals = None

    def __hash__(self):
        return hash(self.field.tobytes()) ^ hash(self.pos)

    def __eq__(self, other):
        hash(self) == hash(other)

    def has_won(self):
        return self.field[self.pos] == self.HOME

    def copy(self):
        copy = PushyState((self.width, self.height), pos=self.pos)
        copy.field = self.field.copy()
        return copy

    def in_bounds(self, pos):
        return 0 <= pos[0] < self.width and 0 <= pos[1] < self.height

    def move(self, direction):
        if self.portals is None:
            self.portals = [
                (x, y) for x, y in zip(*np.where(self.field == self.PORTAL))
            ]

        new_pos = (self.pos[0] + direction[0], self.pos[1] + direction[1])
        if self.in_bounds(new_pos):
            if self.field[new_pos] == self.EMPTY:
                self.pos = new_pos
                return 0
            elif self.field[new_pos] == self.BOX:
                new_box_pos = (new_pos[0] + direction[0], new_pos[1] + direction[1])
                if (
                    self.in_bounds(new_box_pos)
                    and self.field[new_box_pos] == self.EMPTY
                ):
                    self.field[new_pos] = self.EMPTY
                    self.field[new_box_pos] = self.BOX
                    self.pos = new_pos
                    return 1
            elif self.field[new_pos] == self.BALL:
                new_box_pos = (new_pos[0] + direction[0], new_pos[1] + direction[1])
                if self.in_bounds(new_box_pos):
                    if self.field[new_box_pos] == self.EMPTY:
                        self.field[new_pos] = self.EMPTY
                        self.field[new_box_pos] = self.BALL
                        self.pos = new_pos
                        return 1
                    elif self.field[new_box_pos] == self.GOAL:
                        self.field[new_pos] = self.EMPTY
                        self.pos = new_pos
                        return 1
            elif self.field[new_pos] == self.PORTAL:
                for pos in self.portals:
                    if pos != new_pos:
                        self.pos = pos
                        return 1
            elif self.field[new_pos] == self.HOME:
                if not np.any(self.field == self.BALL):
                    self.pos = new_pos
                return 0
        return 0

    def __str__(self):
        out = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                c = {
                    self.EMPTY: " ",
                    self.WALL: "#",
                    self.BOX: "b",
                    self.HOME: "H",
                    self.PORTAL: "@",
                    self.BALL: "?",
                    self.GOAL: "!",
                }[self.field[x, y]]
                if self.pos == (x, y):
                    c = "O"
                line.append(c)
            out.append(" ".join(line))
        return "\n".join(out)


class GameStarter:
    def __init__(self, parent, index):
        self.parent = parent
        self.index = index

    def __call__(self, io):
        self.parent.idx = self.index
        self.parent.save_value("index", self.index)
        self.parent.state = self.parent.MID_GAME
        self.parent.load_field()


class Pushy(core.Game):
    # Directions
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    LEVEL_FOLDER = os.path.join("resources", "misc", "pushy")

    def __init__(self, *args, **kwargs):
        super().__init__()
        # fields = self.load_value("fields")
        fields = []
        for file in os.listdir(self.LEVEL_FOLDER):
            if file.endswith(".json") and not "scored" in file:
                with open(os.path.join(self.LEVEL_FOLDER, file)) as f:
                    fields = fields + json.load(f)

        fields_by_steps = {}
        for field in fields:
            if field["steps"] not in fields_by_steps:
                fields_by_steps[field["steps"]] = []
            fields_by_steps[field["steps"]].append(field)

        self.fields = []
        for steps, fields in sorted(fields_by_steps.items()):
            self.fields.append(max(fields, key=lambda x: x["fu_ratio"]))
        # pprint(self.fields)

        self.idx = self.load_value("index", 0)

        choices = [
            Choice(str(i), (255, 255, 255), GameStarter(self, i))
            for i in range(len(self.fields))
        ]

        self.chooser = SlidingChoice(choices, 5, speed=5)
        self.chooser.index.set_value(self.idx)

        # self.fields = sorted(
        #     fields, key=lambda x: x["steps"] + x["fu_ratio"] * 50, reverse=True
        # )
        self.portal_hue = animations.Ticker(speed=0.2)

    @staticmethod
    def get_line(l):
        l = l.strip()
        out = []
        for x in range(0, len(l), 2):
            out.append(l[x])
        return "".join(out)

    def load_field(self):
        field = self.fields[self.idx]
        pprint(field)
        f = np.array(field["field"], dtype=np.uint8)
        self.field = PushyState(f.shape, pos=tuple(field["start"]))
        self.field.field = f
        self.reset_field = self.field.copy()

    def reset(self, io):
        self.load_field()

    def _update_pregame(self, io, delta):
        io.display.fill((0, 0, 0))
        self.chooser.update(io, delta)

    def _update_midgame(self, io, delta):
        self.field = self.field.copy()
        if io.controller.button_up.fresh_press():
            self.field.move(self.UP)
        if io.controller.button_down.fresh_press():
            self.field.move(self.DOWN)
        if io.controller.button_left.fresh_press():
            self.field.move(self.LEFT)
        if io.controller.button_right.fresh_press():
            self.field.move(self.RIGHT)

        if io.controller.button_b.fresh_release():
            self.field = self.reset_field.copy()

        if io.controller.button_menu.fresh_press():
            self.state = self.PRE_GAME
            self.chooser.index.set_value(self.idx)
            # self.chooser.scroll_offset = animations.AnimatedValue(0)
            return

        if self.field.has_won():
            self.idx = (self.idx + 1) % len(self.fields)
            self.save_value("index", self.idx)
            self.load_field()

        io.display.fill(BLACK)

        left = (io.display.width - self.field.width) // 2
        top = (io.display.height - self.field.height) // 2

        self.portal_hue.tick(delta)
        for fx in range(self.field.width):
            for fy in range(self.field.height):
                x = fx + left
                y = fy + top
                if self.field.field[fx, fy] == self.field.WALL:
                    io.display.update(x, y, Color(64, 64, 64))
                elif self.field.field[fx, fy] == self.field.BOX:
                    io.display.update(x, y, Color(128, 64, 0))
                elif self.field.field[fx, fy] == self.field.HOME:
                    io.display.update(x, y, Color(255, 0, 0))
                elif self.field.field[fx, fy] == self.field.BALL:
                    io.display.update(x, y, Color(0, 128, 128))
                elif self.field.field[fx, fy] == self.field.GOAL:
                    io.display.update(x, y, Color(0, 0, 255))
                elif self.field.field[fx, fy] == self.field.PORTAL:
                    io.display.update(
                        x, y, Color.from_hsv(self.portal_hue.progression, 1, 1)
                    )

        io.display.update(
            self.field.pos[0] + left, self.field.pos[1] + top, GREEN * 0.5
        )


def solveable(field):
    seen = {hash(field)}
    stack = [field]

    while len(stack) > 0:
        field = stack[-1]
        stack = stack[:-1]

        for direction in [Pushy.UP, Pushy.DOWN, Pushy.LEFT, Pushy.RIGHT]:
            new_field = field.copy()
            new_field.move(direction)
            h = hash(new_field)

            if h not in seen:
                if new_field.has_won():
                    return True
                seen.add(h)
                stack.append(new_field)
    return False


class Node:
    def __init__(self, field, parent, cost=1):
        self.field = field
        self.winnable = field.has_won()
        self.parent = parent
        if parent is not None:
            self.distance = parent.distance + cost
            self.reached_by = {parent}
        else:
            self.distance = cost
            self.reached_by = set()


def difficulty(field):
    node = Node(field, None, cost=0)
    seen = {hash(field): node}
    dups = 0
    stack = [node]

    while len(stack) > 0:
        parent = stack[-1]
        stack = stack[:-1]

        for direction in [Pushy.UP, Pushy.DOWN, Pushy.LEFT, Pushy.RIGHT]:
            new_field = parent.field.copy()
            cost = new_field.move(direction)
            child = Node(new_field, parent, cost)
            h = hash(new_field)

            if h not in seen:
                seen[h] = child
                stack.append(child)
            else:
                if child.distance < seen[h].distance:
                    child.reached_by |= seen[h].reached_by
                    seen[h] = child
                    stack.append(child)
                    dups += 1
                else:
                    seen[h].reached_by |= child.reached_by

    winning_nodes = [node for node in seen.values() if node.winnable]
    if len(winning_nodes) == 0:
        return 0, 0, 0

    distance = min([node.distance for node in winning_nodes])
    stack = winning_nodes
    n_winnable = len(winning_nodes)
    while len(stack) > 0:
        node = stack[-1]
        stack = stack[:-1]
        for pred in node.reached_by:
            if not pred.winnable:
                pred.winnable = True
                n_winnable += 1
                stack.append(pred)

    return len(seen), distance, 1 - n_winnable / (len(seen) + dups)


def place_obstacles(field, n, obstacles):
    if n == 0:
        return field

    field = place_obstacles(field, n - 1, obstacles)
    coords = list(zip(*np.where(field.field == field.EMPTY)))
    random.shuffle(obstacles)
    random.shuffle(coords)

    for obstacle in obstacles:
        for x, y in coords:
            if (x, y) != field.pos:
                new_field = field.copy()
                new_field.set(x, y, obstacle)
                if solveable(new_field):
                    return new_field
    return field


def place_obstacles_optimally(field, n, obstacles, fu_weight=15):
    if n == 0:
        return field

    best_fields = None
    best_score = None
    for x, y in zip(*np.where(field.field == field.EMPTY)):
        if (x, y) != field.pos:
            for obstacle in obstacles:
                new_field = field.copy()
                new_field.set(x, y, obstacle)
                new_field = place_obstacles_optimally(
                    new_field, n - 1, obstacles, fu_weight=fu_weight
                )
                if new_field is None:
                    score = None
                else:
                    n_nodes, distance, fu_ratio = difficulty(new_field)
                    score = distance + fu_weight * fu_ratio
                if score is not None and (best_score is None or best_score < score):
                    best_score = score
                    best_fields = [new_field]
                elif score is not None and best_score == score:
                    best_fields.append(new_field)
    if best_fields is None:
        return None, -1
    else:
        return random.choice(best_fields), best_score


def random_field(shape, wall_fill=0.2, total_fill=0.9):
    field = PushyState(shape)
    for x in range(field.width):
        field.set(x, 0, field.WALL)
        field.set(x, field.height - 1, field.WALL)
    for y in range(field.height):
        field.set(0, y, field.WALL)
        field.set(field.width - 1, y, field.WALL)

    field.pos = (1, 1)
    field.set(field.width - 2, field.height - 2, field.HOME)

    n_fields = field.width * field.height - 2 * field.width - 2 * field.height + 2

    last = field

    while field is not None and np.sum(field.field[1:-1, 1:-1] == field.PORTAL) < 2:
        last = field
        field = place_obstacles(field, 1, [field.PORTAL])

    field = place_obstacles(field, 1, [field.GOAL])
    field = place_obstacles(field, 1, [field.BALL])
    field = place_obstacles(field, 1, [field.BALL])

    while (
        field is not None
        and np.sum(field.field[1:-1, 1:-1] != field.EMPTY) / n_fields < wall_fill
    ):
        # print(field)
        last = field
        field = place_obstacles(field, 1, [field.WALL])
    if field is None:
        return last

    best = last
    best_score = 0

    while (
        field is not None
        and np.sum(field.field != field.EMPTY) / (field.width * field.height)
        < total_fill
    ):
        field, score = place_obstacles_optimally(field, 1, [field.BOX])
        if score > best_score:
            best = field

    return best


if __name__ == "__main__":
    sizes = [(x, y) for x in range(5, 10) for y in range(x, 15)]
    sizes = sorted(sizes, key=lambda x: x[0] * x[1])

    best = None
    best_score = None
    best_info = None

    for w, h in sizes:
        file = f"fields_{w}x{h}.json"

        fields = []
        if os.path.exists(file):
            with open(file) as f:
                fields = json.load(f)

        try:
            print(f"Trying {w}x{h}")
            for i in range(100):
                if len(fields) < i:
                    field = random_field((w, h))
                    n_nodes, distance, fu_ratio = difficulty(field)
                    score = distance + fu_ratio * 15
                    fields.append(
                        {
                            "steps": distance,
                            "start": field.pos,
                            "fu_ratio": fu_ratio,
                            "field": [[int(e) for e in c] for c in field.field],
                        }
                    )

                    if best_score is None or score > best_score:
                        best_score = score
                        best = field
                        print()
                        print(
                            f"Best score: {best_score:.1f} (s:{best.width}x{best.height} d:{distance}, n:{n_nodes}, f:{fu_ratio:.2f})"
                        )
                        print(best)

                    with open(file, "w+") as f:
                        json.dump(fields, f)
        finally:
            with open(file, "w+") as f:
                json.dump(fields, f)
                # print()
                # print(f"Current ({w}x{h}):", score)
                # print(field)

    fields = []
    for file in os.listdir():
        if file.endswith(".json") and not "scored" in file:
            with open(file) as f:
                fields = fields + json.load(f)

    # total = len(fields)
    # for i, json_field in enumerate(fields):
    #     print(i, total, end="\r")
    #     f = np.array(json_field["field"], dtype=np.uint8)
    #     field = PushyState(f.shape, pos=tuple(json_field["start"]))
    #     field.field = f
    #     n_nodes, distance, fu_ratio = difficulty(field)
    #     json_field["n_nodes"] = n_nodes
    #     json_field["fu_ratio"] = fu_ratio
    #     json_field["steps"] = distance

    # with open("scored.json", "w+") as f:
    #    json.dump(fields, f)
