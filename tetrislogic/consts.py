# -*- coding: utf-8 -*-
from .utils import Coord, T_Spin


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
FALLING_PIECE_COORD = Coord(4, LINES)

# Scores
LINES_CLEAR_NAME = "LINES_CLEAR_NAME"
SCORES = (
    {LINES_CLEAR_NAME: "", T_Spin.NONE: 0, T_Spin.MINI: 1, T_Spin.T_SPIN: 4},
    {LINES_CLEAR_NAME: "SINGLE", T_Spin.NONE: 1, T_Spin.MINI: 2, T_Spin.T_SPIN: 8},
    {LINES_CLEAR_NAME: "DOUBLE", T_Spin.NONE: 3, T_Spin.T_SPIN: 12},
    {LINES_CLEAR_NAME: "TRIPLE", T_Spin.NONE: 5, T_Spin.T_SPIN: 16},
    {LINES_CLEAR_NAME: "TETRIS", T_Spin.NONE: 8},
)
