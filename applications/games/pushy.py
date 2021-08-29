from IO.color import Color, BLACK, GREEN
from applications.games import core
from helpers import animations
import random
import numpy as np
import json
import os

class PushyState:
    EMPTY = 0
    PUSHY=1
    WALL = 2
    BOX = 3
    HOME = 4

    def __init__(self, shape, pos=(0, 0)):
        self.width, self.height = shape
        self.field = np.ones(shape, dtype=np.uint8) * self.EMPTY
        
        self.pos = pos
    
    def set(self, x, y, value):
        self.field[x, y] = value

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
        new_pos = (self.pos[0] + direction[0], self.pos[1] + direction[1])
        if self.in_bounds(new_pos):
            if self.field[new_pos] == self.EMPTY:
                self.pos = new_pos
                return 0
            elif self.field[new_pos] == self.BOX:
                new_box_pos = (new_pos[0] + direction[0], new_pos[1] + direction[1])
                if self.in_bounds(new_box_pos) and self.field[new_box_pos] == self.EMPTY:
                    self.field[new_pos] = self.EMPTY
                    self.field[new_box_pos] = self.BOX
                    self.pos = new_pos
                    return 1
            elif self.field[new_pos] == self.HOME:
                self.pos = new_pos
                return 0
        return 0

    def __str__(self):
        out = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                c = {self.EMPTY:" ", self.WALL:"#", self.BOX:"b", self.HOME:"H"}[self.field[x,y]]
                if self.pos == (x, y):
                    c = "O"
                line.append(c)
            out.append(" ".join(line))
        return "\n".join(out)
                

class Pushy(core.Game):
    # Directions
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def __init__(self, *args, **kwargs):
        super().__init__()
        fields = self.load_value("fields")
        self.fields = sorted(fields, key=lambda x:x["steps"] * x["fu_ratio"], reverse=True)

    @staticmethod
    def get_line(l):
        l=l.strip()
        out = []
        for x in range(0, len(l), 2):
            out.append(l[x])
        return "".join(out)

    def load_field(self):
        field = self.fields[self.idx]
        print(self.fields[self.idx])
        f = np.array(field["field"], dtype=np.uint8)
        self.field = PushyState(f.shape, pos=tuple(field["start"]))
        self.field.field = f
        self.reset_field = self.field.copy()

    def reset(self, io):
        self.idx = 0
        self.load_field()

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

        if self.field.has_won():
            self.idx += 1
            self.load_field()

        io.display.fill(BLACK)

        left = (io.display.width - self.field.width) // 2
        top = (io.display.height - self.field.height) // 2

        for fx in range(self.field.width):
            for fy in range(self.field.height):
                x = fx + left
                y = fy + top
                if self.field.field[fx, fy] == self.field.WALL:
                    io.display.update(x, y, Color(64, 64, 64))
                elif self.field.field[fx, fy] == self.field.BOX:
                    io.display.update(x, y, Color(128, 64, 0))
                elif self.field.field[fx, fy] == self.field.HOME:
                    io.display.update(x, y, Color(0, 128, 128))

        io.display.update(self.field.pos[0]+left, self.field.pos[1]+top, GREEN*0.75)
    def _update_gameover(self, io, delta):
        pass

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
        return 0, 0
    
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

    field = place_obstacles(field, n-1, obstacles)
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

def place_obstacles_optimally(field, n, obstacles, fu_weight=50):
    if n == 0:
        return field

    best_fields = None
    best_score = None
    for x, y in zip(*np.where(field.field == field.EMPTY)):
        if (x, y) != field.pos:
            for obstacle in obstacles:
                new_field = field.copy()
                new_field.set(x, y, obstacle)
                new_field = place_obstacles_optimally(new_field, n-1, obstacles, fu_weight=fu_weight)
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
        return None
    else:
        return random.choice(best_fields)

def random_field(shape, wall_fill=0.2, total_fill=0.8):
    field = PushyState(shape)
    for x in range(field.width):
        field.set(x, 0, field.WALL)
        field.set(x, field.height-1, field.WALL)
    for y in range(field.height):
        field.set(0, y, field.WALL)
        field.set(field.width-1, y, field.WALL)

    field.pos = (1, 1)
    field.set(field.width-2, field.height-2, field.HOME)

    n_fields = field.width * field.height - 2*field.width - 2*field.height + 2

    last = field

    while field is not None and np.sum(field.field[1:-1,1:-1]!=field.EMPTY)/n_fields < wall_fill:
        print(field)
        last = field
        field = place_obstacles(field, 1, [field.WALL, field.BOX])
    if field is None:
        return last

    while field is not None and np.sum(field.field!=field.EMPTY)/(field.width * field.height) < total_fill:
        print(field)
        last = field
        field = place_obstacles_optimally(field, 1, [field.WALL])
        
    if field is None:
        return last    
    return field
    

if __name__ == "__main__":
    """
    sizes = [(x, y) for x in range(5, 10) for y in range(x, 15)]
    sizes = sorted(sizes, key=lambda x:x[0]*x[1])

    best = None
    best_score = None

    for w,h in sizes:
        file = f"fields_{w}x{h}.json"

        fields = []
        if os.path.exists(file):
            with open(file) as f:
                fields = json.load(f)

        for i in range(100):
            if len(fields) < i:
                field = random_field((w, h))
                score = solve2(field)
                fields.append({"steps":score, "start":field.pos, "field":[[int(e) for e in c] for c in field.field]})        

                if best_score is None or score > best_score:
                    best_score = score
                    best = field

                with open(file, "w+") as f:
                    json.dump(fields, f)
                        
                print()
                print(f"Current ({w}x{h}):", score)
                print(field)
                print(f"Best: ({best.width}x{best.height})", best_score)
                print(best)
    """

    fields = []
    for file in os.listdir():
        if file.endswith(".json") and not "scored" in file:
            with open(file) as f:
                fields = fields + json.load(f)      
      
    total = len(fields)
    for i, json_field in enumerate(fields):
        print(i, total, end="\r")
        f = np.array(json_field["field"], dtype=np.uint8)
        field = PushyState(f.shape, pos=tuple(json_field["start"]))
        field.field = f
        n_nodes, distance, fu_ratio = difficulty(field)
        json_field["n_nodes"] = n_nodes
        json_field["fu_ratio"] = fu_ratio
        json_field["steps"] = distance

    with open("scored.json", "w+") as f:
       json.dump(fields, f)
