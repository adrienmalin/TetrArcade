# -*- coding: utf-8 -*-
import pickle

from .utils import Coord, Movement, Rotation, T_Spin, Phase
from .tetromino import Tetromino, T_Tetrimino
from .consts import (
    LINES,
    COLLUMNS,
    NEXT_PIECES,
    LOCK_DELAY,
    FALL_DELAY,
    AUTOREPEAT_DELAY,
    AUTOREPEAT_PERIOD,
    MATRIX_PIECE_COORD,
)


LINES_CLEAR_NAME = "LINES_CLEAR_NAME"
CRYPT_KEY = 987943759387540938469837689379857347598347598379584857934579343


class PieceContainer:
    def __init__(self):
        self.piece = None


class HoldQueue(PieceContainer):
    pass


class Matrix(list, PieceContainer):
    def __init__(self, lines, collumns):
        list.__init__(self)
        PieceContainer.__init__(self)
        self.lines = lines
        self.collumns = collumns
        self.ghost = None

    def reset(self):
        self.clear()
        for y in range(self.lines + 3):
            self.append_new_line()

    def append_new_line(self):
        self.append([None for x in range(self.collumns)])

    def cell_is_free(self, coord):
        return (
            0 <= coord.x < self.collumns and 0 <= coord.y and not self[coord.y][coord.x]
        )


class NextQueue(PieceContainer):
    def __init__(self, nb_pieces):
        super().__init__()
        self.nb_pieces = nb_pieces
        self.pieces = []


class Stats:

    SCORES = (
        {LINES_CLEAR_NAME: "", T_Spin.NONE: 0, T_Spin.MINI: 1, T_Spin.T_SPIN: 4},
        {LINES_CLEAR_NAME: "SINGLE", T_Spin.NONE: 1, T_Spin.MINI: 2, T_Spin.T_SPIN: 8},
        {LINES_CLEAR_NAME: "DOUBLE", T_Spin.NONE: 3, T_Spin.T_SPIN: 12},
        {LINES_CLEAR_NAME: "TRIPLE", T_Spin.NONE: 5, T_Spin.T_SPIN: 16},
        {LINES_CLEAR_NAME: "TETRIS", T_Spin.NONE: 8},
    )

    def _get_score(self):
        return self._score

    def _set_score(self, new_score):
        self._score = new_score
        if self._score > self.high_score:
            self.high_score = self._score

    score = property(_get_score, _set_score)

    def __init__(self):
        self._score = 0
        self.time = 0

    def new_game(self, level):
        self.level = level - 1
        self.score = 0
        self.lines_cleared = 0
        self.goal = 0
        self.time = 0
        self.combo = -1

        self.lock_delay = LOCK_DELAY
        self.fall_delay = FALL_DELAY

    def new_level(self):
        self.level += 1
        self.goal += 5 * self.level
        if self.level <= 20:
            self.fall_delay = pow(0.8 - ((self.level - 1) * 0.007), self.level - 1)
        if self.level > 15:
            self.lock_delay = 0.5 * pow(0.9, self.level - 15)

    def update_time(self):
        self.time += 1

    def pattern_phase(self, t_spin, lines_cleared):
        pattern_name = []
        pattern_score = 0
        combo_score = 0

        if t_spin:
            pattern_name.append(t_spin)
        if lines_cleared:
            pattern_name.append(self.SCORES[lines_cleared][LINES_CLEAR_NAME])
            self.combo += 1
        else:
            self.combo = -1

        if lines_cleared or t_spin:
            pattern_score = self.SCORES[lines_cleared][t_spin]
            self.goal -= pattern_score
            pattern_score *= 100 * self.level
            pattern_name = "\n".join(pattern_name)

        if self.combo >= 1:
            combo_score = (20 if lines_cleared == 1 else 50) * self.combo * self.level

        self.score += pattern_score + combo_score

        return pattern_name, pattern_score, self.combo, combo_score


class TetrisLogic:

    LINES = LINES
    COLLUMNS = COLLUMNS
    NEXT_PIECES = NEXT_PIECES
    AUTOREPEAT_DELAY = AUTOREPEAT_DELAY
    AUTOREPEAT_PERIOD = AUTOREPEAT_PERIOD
    MATRIX_PIECE_COORD = MATRIX_PIECE_COORD

    def __init__(self, lines=LINES, collumns=COLLUMNS, next_pieces=NEXT_PIECES):
        self.stats = Stats()
        self.load_high_score()
        self.phase = Phase.STARTING
        self.held = HoldQueue()
        self.matrix = Matrix(lines, collumns)
        self.next = NextQueue(next_pieces)
        self.autorepeatable_actions = (self.move_left, self.move_right, self.soft_drop)
        self.pressed_actions = []

    def new_game(self, level=1):
        self.stats.new_game(level)

        self.pressed_actions = []
        self.auto_repeat = False

        self.matrix.reset()
        self.next.pieces = [Tetromino() for n in range(self.next.nb_pieces)]
        self.held.piece = None
        self.start(self.stats.update_time, 1)

        self.on_new_game(self.next.pieces)
        self.new_level()

    def on_new_game(self, next_pieces):
        pass

    def new_level(self):
        self.stats.new_level()
        self.on_new_level(self.stats.level)
        self.generation_phase()

    def on_new_level(self, level):
        pass

    def generation_phase(self):
        self.phase = Phase.GENERATION
        self.matrix.piece = self.next.pieces.pop(0)
        self.next.pieces.append(Tetromino())
        self.matrix.piece.coord = self.MATRIX_PIECE_COORD
        self.matrix.ghost = self.matrix.piece.ghost()

        self.on_generation_phase(
            self.matrix, self.matrix.piece, self.matrix.ghost, self.next.pieces
        )
        if not self.move(Movement.DOWN):
            self.game_over()
        else:
            self.restart(self.fall, self.stats.fall_delay)
            self.falling_phase()

    def on_generation_phase(self, matrix, falling_piece, ghost_piece, next_pieces):
        pass

    def falling_phase(self):
        self.phase = Phase.FALLING
        self.matrix.ghost.coord = self.matrix.piece.coord
        for ghost_mino, current_mino in zip(self.matrix.ghost, self.matrix.piece):
            ghost_mino.coord = current_mino.coord
        while self.space_to_move(
            self.matrix.ghost.coord + Movement.DOWN,
            (mino.coord for mino in self.matrix.ghost),
        ):
            self.matrix.ghost.coord += Movement.DOWN

        self.on_falling_phase(self.matrix.piece, self.matrix.ghost)

    def on_falling_phase(self, falling_piece, ghost_piece):
        pass

    def fall(self):
        self.move(Movement.DOWN)

    def move(self, movement, rotated_coords=None, lock=True):
        potential_coord = self.matrix.piece.coord + movement
        if self.space_to_move(
            potential_coord,
            rotated_coords or (mino.coord for mino in self.matrix.piece),
        ):
            self.matrix.piece.coord = potential_coord
            if rotated_coords:
                for mino, coord in zip(self.matrix.piece, rotated_coords):
                    mino.coord = coord
            else:
                if movement != Movement.DOWN:
                    self.matrix.piece.last_rotation_point = None
                if self.phase == Phase.LOCK:
                    self.restart(self.pattern_phase, self.stats.lock_delay)
            self.falling_phase()
            return True
        else:
            if lock and self.phase != Phase.LOCK and movement == Movement.DOWN:
                self.lock_phase()
            return False

    def lock_phase(self):
        self.phase = Phase.LOCK
        self.on_lock_phase(self.matrix.piece)
        self.start(self.pattern_phase, self.stats.lock_delay)

    def on_lock_phase(self, locked_piece):
        pass

    def space_to_move(self, potential_coord, minoes_coord):
        return all(
            self.matrix.cell_is_free(potential_coord + mino_coord)
            for mino_coord in minoes_coord
        )

    def rotate(self, rotation):
        rotated_coords = tuple(
            Coord(rotation * mino.coord.y, -rotation * mino.coord.x)
            for mino in self.matrix.piece
        )
        for rotation_point, liberty_degree in enumerate(
            self.matrix.piece.SRS[rotation][self.matrix.piece.orientation], start=1
        ):
            if self.move(liberty_degree, rotated_coords):
                self.matrix.piece.orientation = (
                    self.matrix.piece.orientation + rotation
                ) % 4
                self.matrix.piece.last_rotation_point = rotation_point
                return True
        else:
            return False

    def hold(self):
        if not self.matrix.piece.hold_enabled:
            return

        self.matrix.piece.hold_enabled = False
        self.stop(self.pattern_phase)
        self.stop(self.fall)
        self.matrix.piece, self.held.piece = self.held.piece, self.matrix.piece

        if self.matrix.piece:
            self.matrix.piece.coord = self.MATRIX_PIECE_COORD
            self.matrix.ghost = self.matrix.piece.ghost()
            self.on_hold(self.held.piece, self.matrix.piece, self.matrix.ghost)
            self.falling_phase()
        else:
            self.generation_phase()
            self.on_hold(self.held.piece, self.matrix.piece, self.matrix.ghost)

    def on_hold(self, held_piece, falling_piece, ghost_piece):
        pass

    def pattern_phase(self):
        self.phase = Phase.PATTERN
        self.matrix.piece.prelocked = False
        self.stop(self.pattern_phase)
        self.stop(self.fall)

        # Piece unlocked
        if self.space_to_move(
            self.matrix.piece.coord + Movement.DOWN,
            (mino.coord for mino in self.matrix.piece),
        ):
            return

        # Game over
        if all(
            (mino.coord + self.matrix.piece.coord).y >= self.matrix.lines
            for mino in self.matrix.piece
        ):
            self.game_over()
            return

        if self.pressed_actions:
            self.auto_repeat = False
            self.stop(self.repeat_action)

        for mino in self.matrix.piece:
            coord = mino.coord + self.matrix.piece.coord
            if coord.y <= self.matrix.lines + 3:
                self.matrix[coord.y][coord.x] = mino
        self.on_locked(self.matrix, self.matrix.piece)

        # T-Spin
        if (
            type(self.matrix.piece) == T_Tetrimino
            and self.matrix.piece.last_rotation_point is not None
        ):
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

        # Clear complete lines
        lines_cleared = 0
        for y, line in reversed(list(enumerate(self.matrix))):
            if all(mino for mino in line):
                lines_cleared += 1
                self.on_line_remove(self.matrix, y)
                self.matrix.pop(y)
                self.matrix.append_new_line()
        if lines_cleared:
            self.stats.lines_cleared += lines_cleared

        pattern_name, pattern_score, nb_combo, combo_score = self.stats.pattern_phase(
            t_spin, lines_cleared
        )
        self.on_pattern_phase(pattern_name, pattern_score, nb_combo, combo_score)

        if self.stats.goal <= 0:
            self.new_level()
        else:
            self.generation_phase()

        if self.pressed_actions:
            self.start(self.repeat_action, self.AUTOREPEAT_DELAY)

    def on_locked(self, matrix, locked_piece):
        pass

    def on_line_remove(self, matrix, y):
        pass

    def on_pattern_phase(self, pattern_name, pattern_score, nb_combo, combo_score):
        pass

    def move_left(self):
        self.move(Movement.LEFT)

    def move_right(self):
        self.move(Movement.RIGHT)

    def rotate_clockwise(self):
        self.rotate(Rotation.CLOCKWISE)

    def rotate_counter(self):
        self.rotate(Rotation.COUNTER)

    def soft_drop(self):
        moved = self.move(Movement.DOWN)
        if moved:
            self.stats.score += 1
        return moved

    def hard_drop(self):
        while self.move(Movement.DOWN, lock=False):
            self.stats.score += 2
        self.pattern_phase()

    T_SLOT_COORDS = (Coord(-1, 1), Coord(1, 1), Coord(-1, 1), Coord(-1, -1))

    def is_t_slot(self, n):
        t_slot_coord = (
            self.matrix.piece.coord
            + self.T_SLOT_COORDS[(self.matrix.piece.orientation + n) % 4]
        )
        return not self.matrix.cell_is_free(t_slot_coord)

    def pause(self):
        self.phase = Phase.PAUSED
        self.stop_all()
        self.pressed_actions = []
        self.auto_repeat = False
        self.stop(self.repeat_action)

    def resume(self):
        self.phase = Phase.FALLING
        self.start(self.fall, self.stats.fall_delay)
        if self.phase == Phase.LOCK:
            self.start(self.pattern_phase, self.stats.lock_delay)
        self.start(self.stats.update_time, 1)

    def game_over(self):
        self.phase = Phase.OVER
        self.stop_all()
        self.save_high_score()
        self.on_game_over()

    def on_game_over(self):
        pass

    def stop_all(self):
        self.stop(self.fall)
        self.stop(self.pattern_phase)
        self.stop(self.stats.update_time)

    def do_action(self, action):
        action()
        if action in self.autorepeatable_actions:
            self.auto_repeat = False
            self.pressed_actions.append(action)
            if action == self.soft_drop:
                delay = self.stats.fall_delay / 20
            else:
                delay = self.AUTOREPEAT_DELAY
            self.restart(self.repeat_action, delay)

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
            self.stats.high_score = crypted_high_score ^ CRYPT_KEY
        else:
            raise Warning(
                """TetrisLogic.load_high_score not implemented.
High score is set to 0"""
            )
            self.stats.high_score = 0

    def save_high_score(self):
        crypted_high_score = self.stats.high_score ^ CRYPT_KEY
        crypted_high_score = pickle.dumps(crypted_high_score)
        return crypted_high_score

    def start(task, period):
        raise Warning("TetrisLogic.start is not implemented.")

    def stop(self, task):
        raise Warning("TetrisLogic.stop is not implemented.")

    def restart(self, task, period):
        self.stop(task)
        self.start(task, period)
