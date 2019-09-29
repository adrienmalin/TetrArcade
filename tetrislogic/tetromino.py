# -*- coding: utf-8 -*-
import random

from .utils import Coord, Rotation

class Mino:

    def __init__(self, color, coord):
        self.color = color
        self.coord = coord


class Tetromino:

    random_bag = []


    class MetaTetromino(type):

        def __init__(cls, name, bases, dico):
            super().__init__(name, bases, dico)
            cls.classes.append(cls)


    class AbstractTetromino(list):

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
        classes = []

        def __init__(self):
            super().__init__(
                Mino(self.MINOES_COLOR, coord)
                for coord in self.MINOES_COORDS
            )
            self.orientation = 0
            self.last_rotation_point = None
            self.hold_enabled = True
            self.prelocked = False

        def ghost(self):
            return self.__class__()

    class O(AbstractTetromino, metaclass=MetaTetromino):

        SRS = {
            Rotation.CLOCKWISE: (tuple(), tuple(), tuple(), tuple()),
            Rotation.COUNTER: (tuple(), tuple(), tuple(), tuple()),
        }
        MINOES_COORDS = (Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1))
        MINOES_COLOR = "yellow"

        def rotate(self, direction):
            return False


    class I(AbstractTetromino, metaclass=MetaTetromino):

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
        MINOES_COLOR = "cyan"


    class T(AbstractTetromino, metaclass=MetaTetromino):

        MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 0))
        MINOES_COLOR = "magenta"


    class L(AbstractTetromino, metaclass=MetaTetromino):

        MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(1, 1))
        MINOES_COLOR = "orange"


    class J(AbstractTetromino, metaclass=MetaTetromino):

        MINOES_COORDS = (Coord(-1, 1), Coord(-1, 0), Coord(0, 0), Coord(1, 0))
        MINOES_COLOR = "blue"


    class S(AbstractTetromino, metaclass=MetaTetromino):

        MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 1))
        MINOES_COLOR = "green"


    class Z(AbstractTetromino, metaclass=MetaTetromino):

        MINOES_COORDS = (Coord(-1, 1), Coord(0, 1), Coord(0, 0), Coord(1, 0))
        MINOES_COLOR = "red"


    def __new__(cls):
        if not cls.random_bag:
            cls.random_bag = list(Tetromino.AbstractTetromino.classes)
            random.shuffle(cls.random_bag)
        return cls.random_bag.pop()()