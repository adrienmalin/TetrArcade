# -*- coding: utf-8 -*-
import random
import pickle

from .utils import Coord, Movement, Rotation, T_Spin
from .tetromino import Tetromino, T_Tetrimino, I_Tetrimino
from .consts import (
    NB_LINES,
    NB_COLS,
    NB_NEXT,
    LOCK_DELAY,
    FALL_DELAY,
    AUTOREPEAT_DELAY,
    AUTOREPEAT_PERIOD,
    CURRENT_COORD,
    NEXT_COORDS,
    HELD_COORD,
)


LINES_CLEAR_NAME = "LINES_CLEAR_NAME"
CRYPT_KEY = 987943759387540938469837689379857347598347598379584857934579343


class State:

    STARTING = "STARTING"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    OVER = "OVER"


class PieceContainer:

    def __init__(self):
        self.piece = None


class HoldQueue(PieceContainer):
    pass


class Matrix(list, PieceContainer):

    def __init__(self, *args, **kargs):
        list.__init__(self, *args, **kargs)
        PieceContainer.__init__(self)

    def cell_is_free(self, coord):
        return 0 <= coord.x < NB_COLS and 0 <= coord.y and not self[coord.y][coord.x]


class NextQueue(PieceContainer):

    def __init__(self):
        super().__init__()
        self.pieces = []


class TetrisLogic:

    NB_LINES = NB_LINES
    NB_COLS = NB_COLS
    NB_NEXT = NB_NEXT
    LOCK_DELAY = LOCK_DELAY
    FALL_DELAY = FALL_DELAY
    AUTOREPEAT_DELAY = AUTOREPEAT_DELAY
    AUTOREPEAT_PERIOD = AUTOREPEAT_PERIOD
    CURRENT_COORD = CURRENT_COORD
    NEXT_COORDS = NEXT_COORDS
    HELD_COORD = HELD_COORD
    random_bag = []

    def __init__(self):
        self.load_high_score()
        self.state = State.STARTING
        self.held = HoldQueue()
        self.matrix = Matrix()
        self.matrix.ghost = None
        self.next = NextQueue()
        self.time = 0
        self.autorepeatable_actions = (self.move_left, self.move_right, self.soft_drop)
        self.pressed_actions = []
        self._score = 0

    def get_score(self):
        return self._score

    def set_score(self, new_score):
        self._score = new_score
        if self._score > self.high_score:
            self.high_score = self._score

    score = property(get_score, set_score)

    def new_game(self):
        self.level = 0
        self.score = 0
        self.nb_lines_cleared = 0
        self.goal = 0
        self.time = 0

        self.pressed_actions = []
        self.auto_repeat = False

        self.lock_delay = self.LOCK_DELAY
        self.fall_delay = self.FALL_DELAY

        self.matrix.clear()
        for y in range(self.NB_LINES + 3):
            self.append_new_line_to_matrix()
        self.next.pieces = [self.new_tetromino() for n in range(self.NB_NEXT)]
        self.held.piece = None
        self.state = State.PLAYING
        self.start(self.update_time, 1)

        self.new_level()

    def new_tetromino(self):
        if not self.random_bag:
            self.random_bag = list(Tetromino.shapes)
            random.shuffle(self.random_bag)
        return self.random_bag.pop()()

    def append_new_line_to_matrix(self):
        self.matrix.append([None for x in range(self.NB_COLS)])

    def new_level(self):
        self.level += 1
        self.goal += 5 * self.level
        if self.level <= 20:
            self.fall_delay = pow(0.8 - ((self.level - 1) * 0.007), self.level - 1)
        if self.level > 15:
            self.lock_delay = 0.5 * pow(0.9, self.level - 15)
        self.show_text("LEVEL\n{:n}".format(self.level))
        self.restart(self.fall, self.fall_delay)
        self.new_matrix_piece()

    def new_matrix_piece(self):
        self.matrix.piece = self.next.pieces.pop(0)
        self.matrix.piece.coord = self.CURRENT_COORD
        self.matrix.ghost = self.matrix.piece.ghost()
        self.move_ghost()
        self.next.pieces.append(self.new_tetromino())
        self.next.pieces[-1].coord = self.NEXT_COORDS[-1]
        for tetromino, coord in zip(self.next.pieces, self.NEXT_COORDS):
            tetromino.coord = coord

        if not self.can_move(self.matrix.piece.coord, (mino.coord for mino in self.matrix.piece)):
            self.game_over()

    def move_left(self):
        self.move(Movement.LEFT)

    def move_right(self):
        self.move(Movement.RIGHT)

    def rotate_clockwise(self):
        self.rotate(Rotation.CLOCKWISE)

    def rotate_counter(self):
        self.rotate(Rotation.COUNTER)

    def move_ghost(self):
        self.matrix.ghost.coord = self.matrix.piece.coord
        for ghost_mino, current_mino in zip(self.matrix.ghost, self.matrix.piece):
            ghost_mino.coord = current_mino.coord
        while self.can_move(self.matrix.ghost.coord + Movement.DOWN, (mino.coord for mino in self.matrix.ghost)):
            self.matrix.ghost.coord += Movement.DOWN

    def soft_drop(self):
        moved = self.move(Movement.DOWN)
        if moved:
            self.score += 1
        return moved

    def hard_drop(self):
        while self.move(Movement.DOWN, prelock=False):
            self.score += 2
        self.lock()

    def fall(self):
        self.move(Movement.DOWN)

    def move(self, movement, prelock=True):
        potential_coord = self.matrix.piece.coord + movement
        if self.can_move(potential_coord, (mino.coord for mino in self.matrix.piece)):
            if self.matrix.piece.prelocked:
                self.restart(self.lock, self.lock_delay)
            self.matrix.piece.coord = potential_coord
            if not movement == Movement.DOWN:
                self.matrix.piece.last_rotation_point = None
            self.move_ghost()
            return True
        else:
            if prelock and not self.matrix.piece.prelocked and movement == Movement.DOWN:
                self.matrix.piece.prelocked = True
                self.start(self.lock, self.lock_delay)
            return False

    def rotate(self, rotation):
        rotated_coords = tuple(Coord(rotation * mino.coord.y, -rotation * mino.coord.x) for mino in self.matrix.piece)
        for rotation_point, liberty_degree in enumerate(self.matrix.piece.SRS[rotation][self.matrix.piece.orientation], start=1):
            potential_coord = self.matrix.piece.coord + liberty_degree
            if self.can_move(potential_coord, rotated_coords):
                if self.matrix.piece.prelocked:
                    self.restart(self.lock, self.lock_delay)
                self.matrix.piece.coord = potential_coord
                for mino, coord in zip(self.matrix.piece, rotated_coords):
                    mino.coord = coord
                self.matrix.piece.orientation = (self.matrix.piece.orientation + rotation) % 4
                self.matrix.piece.last_rotation_point = rotation_point
                self.move_ghost()
                return True
        else:
            return False

    SCORES = (
        {LINES_CLEAR_NAME: "", T_Spin.NONE: 0, T_Spin.MINI: 1, T_Spin.T_SPIN: 4},
        {LINES_CLEAR_NAME: "SINGLE", T_Spin.NONE: 1, T_Spin.MINI: 2, T_Spin.T_SPIN: 8},
        {LINES_CLEAR_NAME: "DOUBLE", T_Spin.NONE: 3, T_Spin.T_SPIN: 12},
        {LINES_CLEAR_NAME: "TRIPLE", T_Spin.NONE: 5, T_Spin.T_SPIN: 16},
        {LINES_CLEAR_NAME: "TETRIS", T_Spin.NONE: 8},
    )

    def lock(self):
        self.matrix.piece.prelocked = False
        self.stop(self.lock)

        # Piece unlocked
        if self.can_move(self.matrix.piece.coord + Movement.DOWN, (mino.coord for mino in self.matrix.piece)):
            return

        # Game over
        if all((mino.coord + self.matrix.piece.coord).y >= self.NB_LINES for mino in self.matrix.piece):
            self.game_over()
            return

        if self.pressed_actions:
            self.auto_repeat = False
            self.restart(self.repeat_action, self.AUTOREPEAT_DELAY)

        # T-Spin
        if type(self.matrix.piece) == T_Tetrimino and self.matrix.piece.last_rotation_point is not None:
            a = self.is_t_slot(0)
            b = self.is_t_slot(1)
            c = self.is_t_slot(3)
            d = self.is_t_slot(2)
            if self.matrix.piece.last_rotation_point == 5 or (a and b and (c or d)):
                t_spin = T_Spin.T_SPIN
            elif c and d and (a or b):
                t_spin = T_Spin.MINI
            else:
                t_spin = T_Spin.NONE
        else:
            t_spin = T_Spin.NONE

        for mino in self.matrix.piece:
            coord = mino.coord + self.matrix.piece.coord
            del mino.coord
            if coord.y <= self.NB_LINES + 3:
                self.matrix[coord.y][coord.x] = mino

        # Clear complete lines
        nb_lines_cleared = 0
        for y, line in reversed(list(enumerate(self.matrix))):
            if all(mino for mino in line):
                nb_lines_cleared += 1
                self.matrix.pop(y)
                self.append_new_line_to_matrix()
        if nb_lines_cleared:
            self.nb_lines_cleared += nb_lines_cleared

        # Scoring
        lock_strings = []
        lock_score = 0

        if t_spin:
            lock_strings.append(t_spin)
        if nb_lines_cleared:
            lock_strings.append(self.SCORES[nb_lines_cleared][LINES_CLEAR_NAME])
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
            ds = (20 if nb_lines_cleared == 1 else 50) * self.combo * self.level
            lock_score += ds
            self.show_text("COMBO x{:n}\n{:n}".format(self.combo, ds))

        self.score += lock_score

        if self.goal <= 0:
            self.new_level()
        else:
            self.new_matrix_piece()

    def can_move(self, potential_coord, minoes_coords):
        return all(self.matrix.cell_is_free(potential_coord + mino_coord) for mino_coord in minoes_coords)

    T_SLOT_COORDS = (Coord(-1, 1), Coord(1, 1), Coord(-1, 1), Coord(-1, -1))

    def is_t_slot(self, n):
        t_slot_coord = self.matrix.piece.coord + self.T_SLOT_COORDS[(self.matrix.piece.orientation + n) % 4]
        return not self.matrix.cell_is_free(t_slot_coord)

    def swap(self):
        if self.matrix.piece.hold_enabled:
            self.matrix.piece.hold_enabled = False
            self.matrix.piece.prelocked = False
            self.stop(self.lock)
            self.matrix.piece, self.held.piece = self.held.piece, self.matrix.piece
            self.held.piece.coord = self.HELD_COORD
            if type(self.held.piece) == I_Tetrimino:
                self.held.piece.coord += Movement.LEFT
            for mino, coord in zip(self.held.piece, self.held.piece.MINOES_COORDS):
                mino.coord = coord

            if self.matrix.piece:
                self.matrix.piece.coord = self.CURRENT_COORD
                self.matrix.ghost = self.matrix.piece.ghost()
                self.move_ghost()
            else:
                self.new_matrix_piece()

    def pause(self):
        self.state = State.PAUSED
        self.stop_all()
        self.pressed_actions = []
        self.auto_repeat = False
        self.stop(self.repeat_action)

    def resume(self):
        self.state = State.PLAYING
        self.start(self.fall, self.fall_delay)
        if self.matrix.piece.prelocked:
            self.start(self.lock, self.lock_delay)
        self.start(self.update_time, 1)

    def game_over(self):
        self.state = State.OVER
        self.stop_all()
        self.save_high_score()

    def stop_all(self):
        self.stop(self.fall)
        self.stop(self.lock)
        self.stop(self.update_time)

    def update_time(self):
        self.time += 1

    def do_action(self, action):
        action()
        if action in self.autorepeatable_actions:
            self.auto_repeat = False
            self.pressed_actions.append(action)
            self.restart(self.repeat_action, self.AUTOREPEAT_DELAY)

    def repeat_action(self):
        if self.pressed_actions:
            self.pressed_actions[-1]()
            if not self.auto_repeat:
                self.auto_repeat = True
                self.restart(self.repeat_action, self.AUTOREPEAT_PERIOD)
        else:
            self.auto_repeat = False
            self.stop(self.repeat_action)

    def remove_action(self, action):
        if action in self.autorepeatable_actions:
            try:
                self.pressed_actions.remove(action)
            except ValueError:
                pass

    def show_text(self, text):
        print(text)
        raise Warning("TetrisLogic.show_text not implemented.")

    def load_high_score(self, crypted_high_score=None):
        if crypted_high_score:
            crypted_high_score = int(pickle.loads(crypted_high_score))
            self.high_score = crypted_high_score ^ CRYPT_KEY
        else:
            raise Warning(
                """TetrisLogic.load_high_score not implemented.
High score is set to 0"""
            )
            self.high_score = 0

    def save_high_score(self):
        crypted_high_score = self.high_score ^ CRYPT_KEY
        crypted_high_score = pickle.dumps(crypted_high_score)
        return crypted_high_score

    def start(task, period):
        raise Warning("TetrisLogic.start is not implemented.")

    def stop(self, task):
        raise Warning("TetrisLogic.stop is not implemented.")

    def restart(self, task, period):
        self.stop(task)
        self.start(task, period)
