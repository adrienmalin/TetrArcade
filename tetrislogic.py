# -*- coding: utf-8 -*-
import random

# Matrix
NB_LINES = 20
NB_COLS = 10
NB_NEXT_PIECES = 5

# Delays (seconds)
LOCK_DELAY = 0.5
FALL_DELAY = 1
AUTOREPEAT_DELAY = 0.220    # Official : 0.300
AUTOREPEAT_PERIOD = 0.010   # Official : 0.010


class Coord:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coord(self.x+other.x, self.y+other.y)


# Piece init coord
MATRIX_PIECE_INIT_COORD = Coord(4, NB_LINES)
NEXT_PIECES_COORDS = [
    Coord(NB_COLS+6, NB_LINES-4*n-3)
    for n in range(NB_NEXT_PIECES)
]
HELD_PIECE_COORD = Coord(-7, NB_LINES-3)
HELD_I_COORD = Coord(-7, NB_LINES-3)


class State:

    STARTING = "starting"
    PLAYING  = "playing"
    PAUSED   = "paused"
    OVER     = "over"


class Movement:

    LEFT  = Coord(-1,  0)
    RIGHT = Coord( 1,  0)
    DOWN  = Coord( 0, -1)


class Rotation:

    CLOCKWISE        =  1
    COUNTERCLOCKWISE = -1


class T_Spin:

    NO_T_SPIN =   ""
    MINI_T_SPIN = "MINI\nT-SPIN"
    T_SPIN =      "T-SPIN"


class AbstractScheduler:

    def start(task, period):
        raise Warning("AbstractScheduler.start is not implemented.")

    def stop(self, task):
        raise Warning("AbstractScheduler.stop is not implemented.")

    def restart(self, task, period):
        self.stop(task)
        self.start(task, period)


class Tetromino:

    random_bag = []


    class MetaTetromino(type):

        def __init__(cls, name, bases, dico):
            super().__init__(name, bases, dico)
            cls.classes.append(cls)


    class AbstractTetromino:

        # Super rotation system
        SRS = {
            Rotation.COUNTERCLOCKWISE: (
                (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
                (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2)),
                (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
                (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, 2), Coord(-1, 2))
            ),
            Rotation.CLOCKWISE: (
                (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
                (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2)),
                (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
                (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, -2), Coord(-1, 2))
            )
        }
        CAN_SPIN = False
        classes = []

        def __init__(self):
            self.coord = NEXT_PIECES_COORDS[-1]
            self.minoes_coords = self.MINOES_COORDS
            self.orientation = 0
            self.last_rotation_point_used = None
            self.hold_enabled = True
            self.prelocked = False

        def ghost(self):
            return self.__class__()


    class O(AbstractTetromino, metaclass=MetaTetromino):

        SRS = {
            Rotation.COUNTERCLOCKWISE: (tuple(), tuple(), tuple(), tuple()),
            Rotation.CLOCKWISE: (tuple(), tuple(), tuple(), tuple())
        }
        MINOES_COORDS = (Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1))
        MINOES_COLOR = "yellow"

        def rotate(self, direction):
            return False


    class I(AbstractTetromino, metaclass=MetaTetromino):

        SRS = {
            Rotation.COUNTERCLOCKWISE: (
                (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2)),
                (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2)),
                (Coord(0, 1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2)),
                (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2))
            ),
            Rotation.CLOCKWISE: (
                (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2)),
                (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2)),
                (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2)),
                (Coord(0, -1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2))
            )
        }
        MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(2, 0))
        MINOES_COLOR = "cyan"


    class T(AbstractTetromino, metaclass=MetaTetromino):

        MINOES_COORDS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 0))
        MINOES_COLOR = "magenta"
        CAN_SPIN = True


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


class TetrisLogic():

    scheduler = AbstractScheduler()

    def __init__(self):
        self.load_high_score()
        self.state = State.STARTING
        self.matrix = []
        self.next_pieces = []
        self.current_piece = None
        self.held_piece = None
        self.time = 0
        self.autorepeatable_actions = (self.move_left, self.move_right, self.soft_drop)
        self.pressed_actions = []

    def new_game(self):
        self.level = 0
        self.score = 0
        self.nb_lines = 0
        self.goal = 0
        self.time = 0

        self.pressed_actions = []
        self.auto_repeat = False

        self.lock_delay = LOCK_DELAY
        self.fall_delay = FALL_DELAY

        self.matrix = []
        for y in range(NB_LINES+3):
            self.append_new_line_to_matrix()
        self.next_pieces = [Tetromino() for i in range(NB_NEXT_PIECES)]
        self.current_piece = None
        self.held_piece = None
        self.state = State.PLAYING
        self.scheduler.start(self.update_time, 1)
        self.new_level()

    def new_level(self):
        self.level += 1
        self.goal += 5 * self.level
        if self.level <= 20:
            self.fall_delay = pow(0.8 - ((self.level-1)*0.007), self.level-1)
        if self.level > 15:
            self.lock_delay = 0.5 * pow(0.9, self.level-15)
        self.show_text("LEVEL\n{:n}".format(self.level))
        self.scheduler.restart(self.fall, self.fall_delay)
        self.new_current_piece()

    def new_current_piece(self):
        self.current_piece = self.next_pieces.pop(0)
        self.current_piece.coord = MATRIX_PIECE_INIT_COORD
        self.ghost_piece = self.current_piece.ghost()
        self.move_ghost()
        self.next_pieces.append(Tetromino())
        for piece, coord in zip (self.next_pieces, NEXT_PIECES_COORDS):
            piece.coord = coord
        if not self.can_move(
            self.current_piece.coord,
            self.current_piece.minoes_coords
        ):
            self.game_over()

    def move_left(self):
        self.move(Movement.LEFT)

    def move_right(self):
        self.move(Movement.RIGHT)

    def rotate_counterclockwise(self):
        self.rotate(Rotation.COUNTERCLOCKWISE)

    def rotate_clockwise(self):
        self.rotate(Rotation.CLOCKWISE)

    def move_ghost(self):
        self.ghost_piece.coord = self.current_piece.coord
        self.ghost_piece.minoes_coords = self.current_piece.minoes_coords
        while self.can_move(
            self.ghost_piece.coord + Movement.DOWN,
            self.ghost_piece.minoes_coords
        ):
            self.ghost_piece.coord += Movement.DOWN

    def soft_drop(self):
        if self.move(Movement.DOWN):
            self.add_to_score(1)
            return True
        else:
            return False

    def hard_drop(self):
        while self.move(Movement.DOWN, prelock=False):
            self.add_to_score(2)
        self.lock()

    def fall(self):
        self.move(Movement.DOWN)

    def move(self, movement, prelock=True):
        potential_coord = self.current_piece.coord + movement
        if self.can_move(potential_coord, self.current_piece.minoes_coords):
            if self.current_piece.prelocked:
                self.scheduler.restart(self.lock, self.lock_delay)
            self.current_piece.coord = potential_coord
            if not movement == Movement.DOWN:
                self.current_piece.last_rotation_point_used = None
            self.move_ghost()
            return True
        else:
            if (
                prelock and not self.current_piece.prelocked
                and movement == Movement.DOWN
            ):
                self.current_piece.prelocked = True
                self.scheduler.start(self.lock, self.lock_delay)
            return False

    def rotate(self, direction):
        rotated_minoes_coords = tuple(
            Coord(direction*mino_coord.y, -direction*mino_coord.x)
            for mino_coord in self.current_piece.minoes_coords
        )
        for rotation_point, liberty_degree in enumerate(
            self.current_piece.SRS[direction][self.current_piece.orientation],
            start = 1
        ):
            potential_coord = self.current_piece.coord + liberty_degree
            if self.can_move(potential_coord, rotated_minoes_coords):
                if self.current_piece.prelocked:
                    self.scheduler.restart(self.lock, self.lock_delay)
                self.current_piece.coord = potential_coord
                self.current_piece.minoes_coords = rotated_minoes_coords
                self.current_piece.orientation = (
                    (self.current_piece.orientation + direction) % 4
                )
                self.current_piece.last_rotation_point_used = rotation_point
                self.move_ghost()
                return True
        else:
            return False

    SCORES = (
        {"name": "", T_Spin.NO_T_SPIN: 0, T_Spin.MINI_T_SPIN: 1, T_Spin.T_SPIN: 4},
        {"name": "SINGLE", T_Spin.NO_T_SPIN: 1, T_Spin.MINI_T_SPIN: 2, T_Spin.T_SPIN: 8},
        {"name": "DOUBLE", T_Spin.NO_T_SPIN: 3, T_Spin.MINI_T_SPIN: 12},
        {"name": "TRIPLE", T_Spin.NO_T_SPIN: 5, T_Spin.T_SPIN: 16},
        {"name": "TETRIS", T_Spin.NO_T_SPIN: 8}
    )

    def lock(self):
        # Piece unlocked
        if self.move(Movement.DOWN):
            return

        # Start lock
        self.current_piece.prelocked = False
        self.scheduler.stop(self.lock)
        if self.pressed_actions:
            self.auto_repeat = False
            self.scheduler.restart(self.repeat_action, AUTOREPEAT_DELAY)

        # Game over
        if all(
            (mino_coord + self.current_piece.coord).y >= NB_LINES
            for mino_coord in self.current_piece.minoes_coords
        ):
            self.game_over()
            return

        self.enter_the_matrix()

        # Clear complete lines
        nb_lines_cleared = 0
        for y, line in reversed(list(enumerate(self.matrix))):
            if all(mino for mino in line):
                nb_lines_cleared += 1
                self.remove_line_of_matrix(y)
                self.append_new_line_to_matrix()
        if nb_lines_cleared:
            self.nb_lines += nb_lines_cleared

        # T-Spin
        if (
            self.current_piece.CAN_SPIN
            and self.current_piece.last_rotation_point_used is not None
        ):
            a = self.is_t_slot(0)
            b = self.is_t_slot(1)
            c = self.is_t_slot(3)
            d = self.is_t_slot(2)
            if self.current_piece.last_rotation_point_used == 5 or (
                a and b and (c or d)
            ):
                t_spin = T_Spin.T_SPIN
            elif c and d and (a or b):
                t_spin = T_Spin.MINI_T_SPIN
            else:
                t_spin = T_Spin.NO_T_SPIN
        else:
            t_spin = T_Spin.NO_T_SPIN

        # Scoring
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
            self.show_text("\n".join(lock_strings))


        if self.combo >= 1:
            ds = (20 if nb_lines_cleared==1 else 50) * self.combo * self.level
            lock_score += ds
            self.show_text("COMBO x{:n}\n{:n}".format(self.combo, ds))

        self.add_to_score(lock_score)

        if self.goal <= 0:
            self.new_level()
        else:
            self.new_current_piece()

    def enter_the_matrix(self):
        for mino_coord in self.current_piece.minoes_coords:
            coord = mino_coord + self.current_piece.coord
            if coord.y <= NB_LINES+3:
                self.matrix[coord.y][coord.x] = self.current_piece.MINOES_COLOR


    def append_new_line_to_matrix(self):
        self.matrix.append([None for x in range(NB_COLS)])

    def remove_line_of_matrix(self, line):
        self.matrix.pop(line)

    def can_move(self, potential_coord, minoes_coords):
        return all(
            self.cell_is_free(potential_coord+mino_coord)
            for mino_coord in minoes_coords
        )

    def cell_is_free(self, coord):
        return (
            0 <= coord.x < NB_COLS
            and 0 <= coord.y
            and not self.matrix[coord.y][coord.x]
        )

    T_SLOT_COORDS = (
        Coord(-1,  1),
        Coord( 1,  1),
        Coord(-1,  1),
        Coord(-1, -1)
    )

    def is_t_slot(self, n):
        t_slot_coord = self.current_piece.coord + self.T_SLOT_COORDS[
            (self.current_piece.orientation + n) % 4
        ]
        return not self.cell_is_free(t_slot_coord)

    def add_to_score(self, delta_score):
        self.score += delta_score
        if self.score > self.high_score:
            self.high_score = self.score

    def swap(self):
        if self.current_piece.hold_enabled:
            self.current_piece.hold_enabled = False
            self.current_piece.prelocked = False
            self.scheduler.stop(self.lock)
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
            if self.held_piece.__class__ == Tetromino.I:
                self.held_piece.coord = HELD_I_COORD
            else:
                self.held_piece.coord = HELD_PIECE_COORD
            self.held_piece.minoes_coords = self.held_piece.MINOES_COORDS
            if self.current_piece:
                self.current_piece.coord = MATRIX_PIECE_INIT_COORD
                self.ghost_piece = self.current_piece.ghost()
                self.move_ghost()
            else:
                self.new_current_piece()

    def pause(self):
        self.state = State.PAUSED
        self.scheduler.stop(self.fall)
        self.scheduler.stop(self.lock)
        self.scheduler.stop(self.update_time)
        self.pressed_actions = []
        self.auto_repeat = False
        self.scheduler.stop(self.repeat_action)

    def resume(self):
        self.state = State.PLAYING
        self.scheduler.start(self.fall, self.fall_delay)
        if self.current_piece.prelocked:
            self.scheduler.start(self.lock, self.lock_delay)
        self.scheduler.start(self.update_time, 1)

    def game_over(self):
        self.state = State.OVER
        self.scheduler.stop(self.fall)
        self.scheduler.stop(self.update_time)
        self.scheduler.stop(self.repeat_action)
        self.save_high_score()

    def update_time(self):
        self.time += 1

    def do_action(self, action):
        action()
        if action in self.autorepeatable_actions:
            self.auto_repeat = False
            self.pressed_actions.append(action)
            self.scheduler.restart(self.repeat_action, AUTOREPEAT_DELAY)

    def repeat_action(self):
        if self.pressed_actions:
            self.pressed_actions[-1]()
            if not self.auto_repeat:
                self.auto_repeat = True
                self.scheduler.restart(self.repeat_action, AUTOREPEAT_PERIOD)
        else:
            self.auto_repeat = False
            self.scheduler.stop(self.repeat_action)

    def remove_action(self, action):
        if action in self.autorepeatable_actions:
            try:
                self.pressed_actions.remove(action)
            except ValueError:
                pass

    def show_text(self, text):
        print(text)
        raise Warning("TetrisLogic.show_text not implemented.")

    def load_high_score(self):
        self.high_score = 0
        raise Warning(
            """TetrisLogic.load_high_score not implemented.
High score is set to 0"""
        )

    def save_high_score(self):
        raise Warning(
            """TetrisLogic.save_high_score not implemented.
High score is not saved"""
        )

