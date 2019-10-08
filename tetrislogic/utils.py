# -*- coding: utf-8 -*-
class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __matmul__(self, spin):
        return Coord(spin * self.y, -spin * self.x)


class Movement:

    LEFT = Coord(-1, 0)
    RIGHT = Coord(1, 0)
    DOWN = Coord(0, -1)


class Spin:

    CLOCKWISE = 1
    COUNTER = -1


class T_Spin:

    NONE = ""
    MINI = "MINI\nT-SPIN"
    T_SPIN = "T-SPIN"


class T_Slot:

    A = 0
    B = 1
    C = 3
    D = 2


class Color:

    BLUE = 0
    CYAN = 1
    GREEN = 2
    MAGENTA = 3
    ORANGE = 4
    RED = 5
    YELLOW = 6
