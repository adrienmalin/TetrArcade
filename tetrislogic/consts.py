# -*- coding: utf-8 -*-
from .utils import Coord


# Matrix
NB_LINES = 20
NB_COLS = 10
NB_NEXT = 5

# Delays (seconds)
LOCK_DELAY = 0.5
FALL_DELAY = 1
AUTOREPEAT_DELAY = 0.300  # Official : 0.300 s
AUTOREPEAT_PERIOD = 0.010  # Official : 0.010 s

# Piece init coord
MATRIX_PIECE_COORD = Coord(4, NB_LINES)
NEXT_PIECE_COORDS = [Coord(NB_COLS + 4, NB_LINES - 4 * n - 3) for n in range(NB_NEXT)]
HELD_PIECE_COORD = Coord(-5, NB_LINES - 3)
