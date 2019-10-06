# -*- coding: utf-8 -*-
class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)


class Movement:

    LEFT = Coord(-1, 0)
    RIGHT = Coord(1, 0)
    DOWN = Coord(0, -1)


class Rotation:

    CLOCKWISE = 1
    COUNTER = -1


class T_Spin:

    NONE = ""
    MINI = "MINI\nT-SPIN"
    T_SPIN = "T-SPIN"


class Color:

    BLUE = 0
    CYAN = 1
    GREEN = 2
    MAGENTA = 3
    ORANGE = 4
    RED = 5
    YELLOW = 6


class Phase:

    STARTING = "STARTING"
    FALLING = "FALLING"
    LOCK = "LOCK"
    PATTERN = "PATTERN"
    PAUSED = "PAUSED"
    OVER = "OVER"
