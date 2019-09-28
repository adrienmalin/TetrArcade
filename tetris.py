# -*- coding: utf-8 -*-
import random


# Matrix
NB_LINES = 20
NB_COLS = 10
NB_NEXT_PIECES = 5

# Delays (seconds)
LOCK_DELAY = 0.5
FALL_DELAY = 1


class Coord:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coord(self.x+other.x, self.y+other.y)


# Piece init position
MATRIX_PIECE_INIT_POSITION = Coord(4, NB_LINES)
NEXT_PIECES_POSITIONS = [
    Coord(NB_COLS+6, NB_LINES-4*n-3)
    for n in range(NB_NEXT_PIECES)
]
HELD_PIECE_POSITION = Coord(-7, NB_LINES-3)
HELD_I_POSITION = Coord(-7, NB_LINES-3)


class Status:

    STARTING = "starting"
    PLAYING  = "playing"
    PAUSED   = "paused"
    OVER     = "over"


class Movement:

    LEFT  = Coord(-1,  0)
    RIGHT = Coord( 1,  0)
    DOWN  = Coord( 0, -1)


class Rotation:

    CLOCKWISE        = -1
    COUNTERCLOCKWISE = 1


class T_Spin:

    NO_T_SPIN =   ""
    MINI_T_SPIN = "MINI T-SPIN"
    T_SPIN =      "T-SPIN"


class Tetromino:


    class TetrominoBase:
        # Super rotation system
        SRS = {
            Rotation.COUNTERCLOCKWISE: (
                (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
                (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, 2), Coord(-1, 2)),
                (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
                (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2))
            ),
            Rotation.CLOCKWISE: (
                (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
                (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, -2), Coord(-1, 2)),
                (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
                (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2))
            )
        }
        lock_delay = LOCK_DELAY
        fall_delay = FALL_DELAY

        def __init__(self):
            self.position = NEXT_PIECES_POSITIONS[-1]
            self.minoes_positions = self.MINOES_POSITIONS
            self.orientation = 0
            self.last_rotation_point_used = None
            self.hold_enabled = True
            self.prelocked = False

        def ghost(self):
            return self.__class__()


    class O(TetrominoBase):

        SRS = {
            Rotation.COUNTERCLOCKWISE: (tuple(), tuple(), tuple(), tuple()),
            Rotation.CLOCKWISE: (tuple(), tuple(), tuple(), tuple())
        }
        MINOES_POSITIONS = (Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1))
        MINOES_COLOR = "yellow"

        def rotate(self, direction):
            return False


    class I(TetrominoBase):

        SRS = {
            Rotation.COUNTERCLOCKWISE: (
                (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2)),
                (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2)),
                (Coord(0, 1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2)),
                (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2))
            ),
            Rotation.CLOCKWISE: (
                (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2)),
                (Coord(0, -1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2)),
                (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2)),
                (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2))
            )
        }
        MINOES_POSITIONS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(2, 0))
        MINOES_COLOR = "cyan"


    class T(TetrominoBase):

        MINOES_POSITIONS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 0))
        MINOES_COLOR = "magenta"


    class L(TetrominoBase):

        MINOES_POSITIONS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(1, 1))
        MINOES_COLOR = "orange"


    class J(TetrominoBase):

        MINOES_POSITIONS = (Coord(-1, 1), Coord(-1, 0), Coord(0, 0), Coord(1, 0))
        MINOES_COLOR = "blue"


    class S(TetrominoBase):

        MINOES_POSITIONS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 1))
        MINOES_COLOR = "green"


    class Z(TetrominoBase):

        MINOES_POSITIONS = (Coord(-1, 1), Coord(0, 1), Coord(0, 0), Coord(1, 0))
        MINOES_COLOR = "red"


    TETROMINOES = (O, I, T, L, J, S, Z)
    random_bag = []

    def __new__(cls):
        if not cls.random_bag:
            cls.random_bag = list(cls.TETROMINOES)
            random.shuffle(cls.random_bag)
        return cls.random_bag.pop()()


class Scheduler:

    def start(task, period):
        raise NotImplementedError

    def stop(self, task):
        raise NotImplementedError


class Tetris():


    T_SLOT = (Coord(-1, 1), Coord(1, 1), Coord(1, -1), Coord(-1, -1))
    SCORES = (
        {"name": "", T_Spin.NO_T_SPIN: 0, T_Spin.MINI_T_SPIN: 1, T_Spin.T_SPIN: 4},
        {"name": "SINGLE", T_Spin.NO_T_SPIN: 1, T_Spin.MINI_T_SPIN: 2, T_Spin.T_SPIN: 8},
        {"name": "DOUBLE", T_Spin.NO_T_SPIN: 3, T_Spin.MINI_T_SPIN: 12},
        {"name": "TRIPLE", T_Spin.NO_T_SPIN: 5, T_Spin.T_SPIN: 16},
        {"name": "TETRIS", T_Spin.NO_T_SPIN: 8}
    )
    scheduler = Scheduler()

    def __init__(self):
        self.high_score = 0
        self.status = Status.STARTING
        self.matrix = []
        self.next_pieces = []
        self.current_piece = None
        self.held_piece = None
        self.time = 0

    def new_game(self):
        self.level = 0
        self.score = 0
        self.nb_lines = 0
        self.goal = 0
        self.time = 0

        self.lock_delay = LOCK_DELAY
        self.fall_delay = FALL_DELAY

        self.matrix = [
            [None for x in range(NB_COLS)]
            for y in range(NB_LINES+3)
        ]
        self.next_pieces = [Tetromino() for i in range(NB_NEXT_PIECES)]
        self.current_piece = None
        self.held_piece = None
        self.status = Status.PLAYING
        self.scheduler.start(self.clock, 1)
        self.new_level()

    def new_level(self):
        self.level += 1
        self.goal += 5 * self.level
        if self.level <= 20:
            self.fall_delay = pow(0.8 - ((self.level-1)*0.007), self.level-1)
        if self.level > 15:
            self.lock_delay = 0.5 * pow(0.9, self.level-15)
        self.show_text("Level\n{:n}".format(self.level))
        self.scheduler.start(self.drop, self.fall_delay)
        self.new_current_piece()

    def new_current_piece(self):
        self.current_piece = self.next_pieces.pop(0)
        self.current_piece.position = MATRIX_PIECE_INIT_POSITION
        self.ghost_piece = self.current_piece.ghost()
        self.move_ghost()
        self.next_pieces.append(Tetromino())
        for piece, position in zip (self.next_pieces, NEXT_PIECES_POSITIONS):
            piece.position = position
        if not self.can_move(
            self.current_piece.position,
            self.current_piece.minoes_positions
        ):
            self.game_over()

    def cell_is_free(self, position):
        return (
            0 <= position.x < NB_COLS
            and 0 <= position.y
            and not self.matrix[position.y][position.x]
        )

    def can_move(self, potential_position, minoes_positions):
        return all(
            self.cell_is_free(potential_position+mino_position)
            for mino_position in minoes_positions
        )

    def move(self, movement, prelock_on_stuck=True):
        potential_position = self.current_piece.position + movement
        if self.can_move(potential_position, self.current_piece.minoes_positions):
            if self.current_piece.prelocked:
                self.scheduler.stop(self.lock)
                self.scheduler.start(self.lock, self.lock_delay)
            self.current_piece.position = potential_position
            self.current_piece.last_rotation_point_used = None
            self.move_ghost()
            return True
        else:
            if (
                prelock_on_stuck and not self.current_piece.prelocked
                and movement == Movement.DOWN
            ):
                self.current_piece.prelocked = True
                self.scheduler.start(self.lock, self.lock_delay)
            return False

    def move_left(self):
        self.move(Movement.LEFT)

    def move_right(self):
        self.move(Movement.RIGHT)

    def rotate(self, direction):
        rotated_minoes_positions = tuple(
            Coord(-direction*mino_position.y, direction*mino_position.x)
            for mino_position in self.current_piece.minoes_positions
        )
        for rotation_point, liberty_degree in enumerate(
            self.current_piece.SRS[direction][self.current_piece.orientation],
            start = 1
        ):
            potential_position = self.current_piece.position + liberty_degree
            if self.can_move(potential_position, rotated_minoes_positions):
                if self.current_piece.prelocked:
                    self.scheduler.stop(self.lock)
                    self.scheduler.start(self.lock, self.lock_delay)
                self.current_piece.position = potential_position
                self.current_piece.minoes_positions = rotated_minoes_positions
                self.current_piece.orientation = (
                    (self.current_piece.orientation + direction) % 4
                )
                self.current_piece.last_rotation_point_used = rotation_point
                self.move_ghost()
                return True
        else:
            return False

    def rotate_counterclockwise(self):
        self.rotate(Rotation.COUNTERCLOCKWISE)

    def rotate_clockwise(self):
        self.rotate(Rotation.CLOCKWISE)

    def move_ghost(self):
        self.ghost_piece.position = self.current_piece.position
        self.ghost_piece.minoes_positions = self.current_piece.minoes_positions
        while self.can_move(
            self.ghost_piece.position + Movement.DOWN,
            self.ghost_piece.minoes_positions
        ):
            self.ghost_piece.position += Movement.DOWN

    def drop(self):
        self.move(Movement.DOWN)

    def add_to_score(self, ds):
        self.score += ds
        if self.score > self.high_score:
            self.high_score = self.score

    def soft_drop(self):
        if self.move(Movement.DOWN):
            self.add_to_score(1)
            return True
        else:
            return False

    def hard_drop(self):
        while self.move(Movement.DOWN, prelock_on_stuck=False):
            self.add_to_score(2)
        self.lock()

    def lock(self):
        if self.move(Movement.DOWN):
            return

        self.current_piece.prelocked = False
        self.scheduler.stop(self.lock)

        if all(
            (mino_position + self.current_piece.position).y >= NB_LINES
            for mino_position in self.current_piece.minoes_positions
        ):
            self.game_over()
            return

        for mino_position in self.current_piece.minoes_positions:
            position = mino_position + self.current_piece.position
            if position.y <= NB_LINES+3:
                self.matrix[position.y][position.x] = self.current_piece.MINOES_COLOR

        nb_lines_cleared = 0
        for y, line in reversed(list(enumerate(self.matrix))):
            if all(mino for mino in line):
                nb_lines_cleared += 1
                self.matrix.pop(y)
                self.matrix.append([None for x in range(NB_COLS)])
        if nb_lines_cleared:
            self.nb_lines += nb_lines_cleared

        if (
            self.current_piece.__class__ == Tetromino.T
            and self.current_piece.last_rotation_point_used is not None
        ):
            position = self.current_piece.position
            orientation = self.current_piece.orientation
            nb_orientations = len(self.current_piece.SRS[Rotation.CLOCKWISE])
            a = not self.cell_is_free(position+self.T_SLOT[orientation])
            b = not self.cell_is_free(position+self.T_SLOT[(orientation-1)%nb_orientations])
            c = not self.cell_is_free(position+self.T_SLOT[(orientation-3)%nb_orientations])
            d = not self.cell_is_free(position+self.T_SLOT[(orientation-2)%nb_orientations])

            if self.current_piece.last_rotation_point_used == 5 or (a and b and (c or d)):
                t_spin = T_Spin.T_SPIN
            elif c and d and (a or b):
                t_spin = T_Spin.MINI_T_SPIN
            else:
                t_spin = T_Spin.NO_T_SPIN
        else:
            t_spin = T_Spin.NO_T_SPIN

        lock_strings = []
        lock_score = 0

        if t_spin:
            lock_strings.append(t_spin)
        if nb_lines_cleared:
            lock_strings.append(self.SCORES[nb_lines_cleared]["name"])
            self.combo += 1
        else:
            self.combo = -1

        if nb_lines_cleared or t_spin:
            ds = self.SCORES[nb_lines_cleared][t_spin]
            self.goal -= ds
            ds *= 100 * self.level
            lock_score += ds
            lock_strings.append(str(ds))

        if self.combo >= 1:
            lock_strings.append("COMBO x%d" % self.combo)
            ds = (20 if nb_lines_cleared==1 else 50) * self.combo * self.level
            lock_score += ds
            lock_strings.append(str(ds))

        if lock_strings:
            self.show_text("\n".join(lock_strings))

        self.add_to_score(lock_score)

        if self.goal <= 0:
            self.scheduler.stop(self.drop)
            self.new_level()
        else:
            self.new_current_piece()

    def swap(self):
        if self.current_piece.hold_enabled:
            self.current_piece.hold_enabled = False
            self.current_piece.prelocked = False
            self.scheduler.stop(self.lock)
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
            if self.held_piece.__class__ == Tetromino.I:
                self.held_piece.position = HELD_I_POSITION
            else:
                self.held_piece.position = HELD_PIECE_POSITION
            self.held_piece.minoes_positions = self.held_piece.MINOES_POSITIONS
            if self.current_piece:
                self.current_piece.position = MATRIX_PIECE_INIT_POSITION
                self.ghost_piece = self.current_piece.ghost()
                self.move_ghost()
            else:
                self.new_current_piece()

    def pause(self):
        self.status = Status.PAUSED
        self.scheduler.stop(self.drop)
        self.scheduler.stop(self.lock)
        self.scheduler.stop(self.clock)
        self.pressed_actions = []
        self.stop_autorepeat()

    def resume(self):
        self.status = Status.PLAYING
        self.scheduler.start(self.drop, self.fall_delay)
        if self.current_piece.prelocked:
            self.scheduler.start(self.lock, self.lock_delay)
        self.scheduler.start(self.clock, 1)

    def clock(self, delta_time=1):
        self.time += delta_time

    def game_over(self):
        self.status = Status.OVER
        self.scheduler.stop(self.drop)
        self.scheduler.stop(self.clock)

    def show_text(self, text):
        print(text)

