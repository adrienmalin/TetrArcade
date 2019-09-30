# -*- coding: utf-8 -*-
class Coord:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coord(self.x+other.x, self.y+other.y)


class Movement:

    LEFT  = Coord(-1,  0)
    RIGHT = Coord( 1,  0)
    DOWN  = Coord( 0, -1)


class Rotation:

    CLOCKWISE =  1
    COUNTER   = -1


class T_Spin:

    NONE =   ""
    MINI = "MINI\nT-SPIN"
    T_SPIN =      "T-SPIN"


class Line(list):
    pass
