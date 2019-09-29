# -*- coding: utf-8 -*-
from .utils import Coord


# Matrix
NB_LINES = 20
NB_COLS = 10
NB_NEXT_PIECES = 5

# Delays (seconds)
LOCK_DELAY = 0.5
FALL_DELAY = 1
AUTOREPEAT_DELAY = 0.200    # Official : 0.300
AUTOREPEAT_PERIOD = 0.010   # Official : 0.010


# Piece init coord
CURRENT_COORD = Coord(4, NB_LINES)
NEXT_COORDS = [
    Coord(NB_COLS+6, NB_LINES-4*n-3)
    for n in range(NB_NEXT_PIECES)
]
HELD_COORD = Coord(-7, NB_LINES-3)
HELD_I_COORD = Coord(-7, NB_LINES-3)