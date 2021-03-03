class ControllerValue:
    def __init__(self, subscribers=[], dtype=bool, default=False):
        self.value = default
        self.dtype = dtype
        self.subscribers = set(subscribers)

    def update(self, value):
        new_value = self.dtype(value)
        if new_value != self.value:
            self.value = new_value
            for fun in self.subscribers:
                fun(self.value)

    def subscribe(self, fun):
        self.subscribers.add(fun)

    def unsubscribe(self, fun):
        if fun in self.subscribers:
            self.subscribers.remove(fun)


class _BaseController:
    ValueClass = ControllerValue

    def __init__(self):
        self.up = self.ValueClass()
        self.right = self.ValueClass()
        self.down = self.ValueClass()
        self.left = self.ValueClass()
        self.a = self.ValueClass()
        self.b = self.ValueClass()
        self.menu = self.ValueClass()

from IO.controller._pygameController import *
from IO.controller._cursesController import *