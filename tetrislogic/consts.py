# -*- coding: utf-8 -*-
from .utils import Coord


# Matrix
LINES = 20
COLLUMNS = 10
NEXT_PIECES = 5

# Delays (seconds)
LOCK_DELAY = 0.5
FALL_DELAY = 1
AUTOREPEAT_DELAY = 0.300  # Official : 0.300 s
AUTOREPEAT_PERIOD = 0.010  # Official : 0.010 s

# Piece init coord
MATRIX_PIECE_COORD = Coord(4, LINES)
