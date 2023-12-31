# -*- coding: utf-8 -*-
import random

from .utils import Coord, Spin, Color


class Mino:
    def __init__(self, color, coord):
        self.color = color
        self.coord = coord


class MetaTetromino(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        Tetromino.shapes.append(cls)


class Tetromino:

    shapes = []
    random_bag = []

    def __new__(cls):
        if not cls.random_bag:
            cls.random_bag = list(cls.shapes)
            random.shuffle(cls.random_bag)
        return cls.random_bag.pop()()


class TetrominoBase(list):

    # Super rotation system
    SRS = {
        Spin.CLOCKWISE: (
            (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
            (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2)),
            (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
            (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, -2), Coord(-1, 2)),
        ),
        Spin.COUNTER: (
            (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
            (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2)),
            (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
            (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, 2), Coord(-1, 2)),
        ),
    }

    def __init__(self):
        super().__init__(Mino(self.MINOES_COLOR, coord) for coord in self.MINOES_COORDS)
        self.orientation = 0
        self.rotated_last = False
        self.rotation_point_5_used = False
        self.hold_enabled = True

    def ghost(self):
        return type(self)()


class O_Tetrimino(TetrominoBase, metaclass=MetaTetromino):

    SRS = {
        Spin.CLOCKWISE: (tuple(), tuple(), tuple(), tuple()),
        Spin.COUNTER: (tuple(), tuple(), tuple(), tuple()),
    }
    MINOES_COORDS = (Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1))
    MINOES_COLOR = Color.YELLOW

    def rotate(self, direction):
        return False


class I_Tetrimino(TetrominoBase, metaclass=MetaTetromino):

    SRS = {
        Spin.CLOCKWISE: (
            (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2)),
            (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2)),
            (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2)),
            (Coord(0, -1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2)),
        ),
        Spin.COUNTER: (
            (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2)),
            (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2)),
            (Coord(0, 1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2)),
            (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2)),
        ),
    }
    MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(2, 0))
    MINOES_COLOR = Color.CYAN


class T_Tetrimino(TetrominoBase, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 0))
    MINOES_COLOR = Color.MAGENTA


class L_Tetrimino(TetrominoBase, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(1, 1))
    MINOES_COLOR = Color.ORANGE


class J_Tetrimino(TetrominoBase, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 1), Coord(-1, 0), Coord(0, 0), Coord(1, 0))
    MINOES_COLOR = Color.BLUE


class S_Tetrimino(TetrominoBase, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 1))
    MINOES_COLOR = Color.GREEN


class Z_Tetrimino(TetrominoBase, metaclass=MetaTetromino):

    MINOES_COORDS = (Coord(-1, 1), Coord(0, 1), Coord(0, 0), Coord(1, 0))
    MINOES_COLOR = Color.RED
