from applications import core
from helpers import textutils, bitmaputils, animations
from IO.color import *
import time
from applications.menu import Menu, SlidingChoice, Choice, ApplicationOpener


class ScrollerEntry:
    def __init__(self, text, color=None, speed=0.2):
        self.text = text.upper()
        if color is None:
            color = WHITE
        self.color = color
        self.speed = speed

    def copy(self):
        return ScrollerEntry(self.text, color=self.color, speed=self.speed)

    def __eq__(self, other):
        return (
            self.text == other.text
            and all(self.color == other.color)
            and self.speed == other.speed
        )

    def to_json(self):
        return {
            "text": self.text,
            "color": list(map(int, self.color)),
            "speed": self.speed,
        }

    @classmethod
    def from_json(cls, json):
        text = json.get("text", " ")
        c = json.get("color", [255, 255, 255])
        if len(c) != 3:
            color = WHITE
        else:
            color = Color(*c)
        speed = json.get("speed", 0.2)
        return cls(text, color=color, speed=speed)


class TextScroller(core.Application):
    def __init__(self, *args, entry=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entry is None:
            self.entry = ScrollerEntry("Hello World!")
        else:
            self.entry = entry
        self.scroll_offset = animations.AnimatedValue(0, speed=self.entry.speed)
        self.bmp = textutils.get_text_bitmap(self.entry.text)
        self.bmp_width = self.bmp.shape[1]

    def update(self, io, delta):
        io.display.fill((0, 0, 0))

        offset = self.scroll_offset.tick(delta)

        if self.scroll_offset.finished():
            self.scroll_offset = animations.AnimatedValue(0, self.entry.speed)
            self.scroll_offset.set_value(self.bmp_width + io.display.width)
            self.bmp = textutils.get_text_bitmap(self.entry.text)
            self.bmp_width = self.bmp.shape[1]

        x = round(io.display.width - offset)

        bitmaputils.apply_bitmap(
            self.bmp,
            io.display,
            (x, io.display.height // 2 - 2),
            fg_color=self.entry.color,
        )


class TextEditor(core.Application):
    LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?:-()<> "
    REPEAT_WAIT = 0.5
    REPEAT_TIME = 0.1

    def __init__(self, *args, entry=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entry is None:
            self.entry = ScrollerEntry("Hello World!")
        else:
            self.entry = entry

        self.entry.text = "".join(
            [c if c in self.LETTERS else "?" for c in self.entry.text]
        )

        if len(self.entry.text) == 0:
            self.entry.text = " "

        self.scroll_offset = animations.AnimatedValue(0, speed=3)
        self.idx = 0
        self.bmp = textutils.get_text_bitmap(self.entry.text)

        self.press_start = 0
        self.last_letter = 0

    def update(self, io, delta):
        io.display.fill((0, 0, 0))

        if io.controller.button_left.fresh_press():
            if self.idx <= 0:
                self.entry.text = " " + self.entry.text
                self.idx = 0
                self.bmp = textutils.get_text_bitmap(self.entry.text)
            else:
                self.idx -= 1

        if io.controller.button_right.fresh_press():
            if self.idx >= len(self.entry.text) - 1:
                self.entry.text += " "
                self.idx = len(self.entry.text) - 1
                self.bmp = textutils.get_text_bitmap(self.entry.text)

            else:
                self.idx += 1

        if io.controller.button_a.fresh_press():
            self.entry.text = (
                self.entry.text[: self.idx + 1] + " " + self.entry.text[self.idx + 1 :]
            )
            self.idx += 1
            self.bmp = textutils.get_text_bitmap(self.entry.text)

        if io.controller.button_b.fresh_press():
            self.entry.text = (
                self.entry.text[: self.idx] + self.entry.text[self.idx + 1 :]
            )
            if len(self.entry.text) == 0:
                self.entry.text = " "
            self.idx = min(len(self.entry.text) - 1, self.idx)
            self.bmp = textutils.get_text_bitmap(self.entry.text)

        if io.controller.button_b.fresh_press():
            if self.idx == len(self.entry.text) - 1:
                self.idx += 1

        if io.controller.button_up.fresh_press():
            letter_idx = self.LETTERS.index(self.entry.text[self.idx])
            letter_idx = (letter_idx + 1) % len(self.LETTERS)
            self.entry.text = (
                self.entry.text[: self.idx]
                + self.LETTERS[letter_idx]
                + self.entry.text[self.idx + 1 :]
            )
            self.bmp = textutils.get_text_bitmap(self.entry.text)
            self.press_start = time.time()
            self.last_letter = time.time()
        elif io.controller.button_down.fresh_press():
            letter_idx = self.LETTERS.index(self.entry.text[self.idx])
            letter_idx = (letter_idx - 1) % len(self.LETTERS)
            self.entry.text = (
                self.entry.text[: self.idx]
                + self.LETTERS[letter_idx]
                + self.entry.text[self.idx + 1 :]
            )
            self.bmp = textutils.get_text_bitmap(self.entry.text)
            self.press_start = time.time()
            self.last_letter = time.time()
        elif (
            io.controller.button_up.get_value()
            and time.time() - self.press_start > self.REPEAT_WAIT
            and time.time() - self.last_letter > self.REPEAT_TIME
        ):
            letter_idx = self.LETTERS.index(self.entry.text[self.idx])
            letter_idx = (letter_idx + 1) % len(self.LETTERS)
            self.entry.text = (
                self.entry.text[: self.idx]
                + self.LETTERS[letter_idx]
                + self.entry.text[self.idx + 1 :]
            )
            self.bmp = textutils.get_text_bitmap(self.entry.text)
            self.last_letter = time.time()
        elif (
            io.controller.button_down.get_value()
            and time.time() - self.press_start > self.REPEAT_WAIT
            and time.time() - self.last_letter > self.REPEAT_TIME
        ):
            letter_idx = self.LETTERS.index(self.entry.text[self.idx])
            letter_idx = (letter_idx - 1) % len(self.LETTERS)
            self.entry.text = (
                self.entry.text[: self.idx]
                + self.LETTERS[letter_idx]
                + self.entry.text[self.idx + 1 :]
            )
            self.bmp = textutils.get_text_bitmap(self.entry.text)
            self.last_letter = time.time()

        self.scroll_offset.set_value(self.idx * 4)

        offset = self.scroll_offset.tick(delta)

        x = round(io.display.width // 2 - 2 - offset)

        bitmaputils.apply_bitmap(
            self.bmp,
            io.display,
            (x, io.display.height // 2 - 2),
            fg_color=WHITE,
            bg_color=WHITE * 0.3,
        )


class ColorPicker(core.Application):
    COLORS = {
        "White": WHITE,
        "Red": RED,
        "Green": GREEN,
        "Blue": BLUE,
        "Yellow": YELLOW,
        "Cyan": CYAN,
        "Magenta": MAGENTA,
    }

    def __init__(self, *args, entry=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entry is None:
            self.entry = ScrollerEntry("Hello World!")
        else:
            self.entry = entry

        self.idx = 0

        self.color_choice = SlidingChoice(
            [Choice(name, color, lambda _: None) for name, color in self.COLORS.items()]
        )

    def update(self, io, delta):
        io.display.fill((0, 0, 0))
        self.color_choice.update(io, delta)
        self.entry.color = list(self.COLORS.values())[round(self.color_choice.prog)]


class SpeedPicker(core.Application):
    SPEEDS = {
        "Very Slow": 0.05,
        "Slow": 0.1,
        "Normal": 0.2,
        "Fast": 0.4,
        "Ver Fast": 0.8,
    }

    def __init__(self, *args, entry=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entry is None:
            self.entry = ScrollerEntry("Hello World!")
        else:
            self.entry = entry

        self.idx = 0

        self.color_choice = SlidingChoice(
            [Choice(name, WHITE, lambda _: None) for name, speed in self.SPEEDS.items()]
        )
        self.color_choice.index.set_value(2)

    def update(self, io, delta):
        io.display.fill((0, 0, 0))
        self.color_choice.update(io, delta)
        self.entry.speed = list(self.SPEEDS.values())[round(self.color_choice.prog)]


class Deleter(core.Application):
    def __init__(self, parent, entry, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.entry = entry

    def update(self, io, delta):
        if self.entry in self.parent.entries:
            self.parent.entries.remove(self.entry)
        else:
            print("Couldn't remove")

        io.close_application()
        io.close_application()
        io.close_application()


class Aborter(core.Application):
    def update(self, io, delta):
        io.close_application()
        io.close_application()


class EntryMenu(Menu):
    def __init__(self, parent, entry, *args, **kwargs):
        self.parent = parent
        self.entry = entry
        applications = [
            TextScroller(entry=entry, name="Show", color=WHITE),
            TextEditor(entry=entry, name="Edit", color=WHITE),
            ColorPicker(entry=entry, name="Color", color=WHITE),
            SpeedPicker(entry=entry, name="Speed", color=WHITE),
            Menu(
                [
                    Aborter(name="Cancel", color=RED),
                    Deleter(parent, entry, name="Confirm", color=RED),
                ],
                name="Delete",
                color=RED,
            ),
        ]

        super().__init__(applications, *args, **kwargs)


class NewEntry(core.Application):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    def update(self, io, delta):
        new_entry = ScrollerEntry(" ")
        self.parent.entries.append(new_entry)
        io.applications[-1] = EntryMenu(
            self.parent,
            new_entry,
            color=new_entry.color,
            name="<Empty>",
        )
        io.applications[-1].update(io, delta)


class Scroller(Menu):
    def __init__(self, entries=None, *args, **kwargs):
        super().__init__([], *args, **kwargs)

        if entries is None:
            entries_json = self.load_value("texts", default=[])
            self.entries = [ScrollerEntry.from_json(j) for j in entries_json]

        if len(self.entries) == 0:
            self.entries = [ScrollerEntry("Hello World")]

        self.displayed_entries = [entry.copy() for entry in self.entries]

        self.entry_len = len(self.entries)
        self.applications = [
            EntryMenu(
                self,
                entry,
                color=entry.color,
                name=entry.text if entry.text.strip() != "" else " ",
            )
            for entry in self.entries
        ] + [NewEntry(self, color=GREEN, name="+")]

        self.args = args
        self.kwargs = kwargs

        super().__init__(self.applications, *args, **kwargs)

    def has_changed(self):
        return len(self.entries) != len(self.displayed_entries) or any(
            [e1 != e2 for e1, e2 in zip(self.entries, self.displayed_entries)]
        )

    def update_entries(self):
        self.save_value("texts", [entry.to_json() for entry in self.entries])
        index = self.chooser.index
        self.__init__(self.entries, *self.args, **self.kwargs)
        self.chooser.index = index
        idx = self.chooser.index.get_value()
        if idx >= len(self.entries):
            self.chooser.index.set_value(len(self.entries) - 1)

    def update(self, io, delta):
        if self.has_changed():
            self.update_entries()

        super().update(io, delta)
