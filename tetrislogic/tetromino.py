# -*- coding: utf-8 -*-
from .utils import Coord, Rotation, Color


class Mino:
    def __init__(self, color, coord):
        self.color = color
        self.coord = coord


class MetaTetromino(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        Tetromino.shapes.append(cls)


class Tetromino(list):

    shapes = []
    # Super rotation system
    SRS = {
        Rotation.CLOCKWISE: (
            (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
            (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2)),
            (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
            (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, -2), Coord(-1, 2)),
        ),
        Rotation.COUNTER: (
            (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
            (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2)),
            (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
            (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, 2), Coord(-1, 2)),
        ),
    }

    def __init__(self):
        super().__init__(Mino(self.MINOES_COLOR, coord) for coord in self.MINOES_COORDS)
        self.orientation = 0
        self.last_rotation_point = None
        self.hold_enabled = True
        self.prelocked = False

    def ghost(self):
        return type(self)()


class O(Tetromino, metaclass=MetaTetromino):

    SRS = {
        Rotation.CLOCKWISE: (tuple(), tuple(), tuple(), tuple()),
        Rotation.COUNTER: (tuple(), tuple(), tuple(), tuple()),
    }
    MINOES_COORDS = (Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1))
    MINOES_COLOR = Color.YELLOW

    def rotate(self, direction):
        return False


class I(Tetromino, metaclass=MetaTetromino):

    SRS = {
        Rotation.CLOCKWISE: (
            (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2)),
            (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2)),
            (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2)),
            (Coord(0, -1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2)),
        ),
        Rotation.COUNTER: (
            (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2)),
            (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2)),
            (Coord(0, 1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2)),
            (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2)),
        ),
    }
    MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(2, 0))
    MINOES_COLOR = Color.CYAN


class T(Tetromino, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 0))
    MINOES_COLOR = Color.MAGENTA


class L(Tetromino, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(1, 1))
    MINOES_COLOR = Color.ORANGE


class J(Tetromino, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 1), Coord(-1, 0), Coord(0, 0), Coord(1, 0))
    MINOES_COLOR = Color.BLUE


class S(Tetromino, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 1))
    MINOES_COLOR = Color.GREEN


class Z(Tetromino, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 1), Coord(0, 1), Coord(0, 0), Coord(1, 0))
    MINOES_COLOR = Color.RED
