# -*- coding: utf-8 -*-
"""Tetris game logic meant to be implemented with GUI
Follows Tetris Guidelines 2009 (see https://tetris.fandom.com/wiki/Tetris_Guideline)
"""


import pickle

from .utils import Coord, Movement, Spin, T_Spin, T_Slot
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
    SCORES,
    LINES_CLEAR_NAME,
)


CRYPT_KEY = 987943759387540938469837689379857347598347598379584857934579343


class AbstractScheduler:
    def postpone(task, delay):
        """schedule callable task once after delay in second"""
        raise Warning("AbstractTimer.postpone is not implemented.")

    def cancel(self, task):
        """cancel task if schedule of pass"""
        raise Warning("AbstractTimer.stop is not implemented.")

    def reset(self, task, period):
        """cancel and reschedule task"""
        self.timer.cancel(task)
        self.timer.postpone(task, period)


class AbstractPieceContainer:
    def __init__(self):
        self.piece = None


class HoldQueue(AbstractPieceContainer):
    pass


class Matrix(list, AbstractPieceContainer):
    def __init__(self, lines, collumns):
        list.__init__(self)
        AbstractPieceContainer.__init__(self)
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

    def space_to_move(self, potential_coord, minoes_coord):
        return all(
            self.cell_is_free(potential_coord + mino_coord)
            for mino_coord in minoes_coord
        )

    def space_to_fall(self):
        return self.space_to_move(
            self.piece.coord + Movement.DOWN, (mino.coord for mino in self.piece)
        )


class NextQueue(AbstractPieceContainer):
    def __init__(self, nb_pieces):
        super().__init__()
        self.nb_pieces = nb_pieces
        self.pieces = []


class Stats:
    def _get_score(self):
        return self._score

    def _set_score(self, new_score):
        self._score = new_score
        if self._score > self.high_score:
            self.high_score = self._score

    score = property(_get_score, _set_score)

    def __init__(self):
        self._score = 0
        self.high_score = 0
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

    def locks_down(self, t_spin, lines_cleared):
        pattern_name = []
        pattern_score = 0
        combo_score = 0

        if t_spin:
            pattern_name.append(t_spin)
        if lines_cleared:
            pattern_name.append(SCORES[lines_cleared][LINES_CLEAR_NAME])
            self.combo += 1
        else:
            self.combo = -1

        if lines_cleared or t_spin:
            pattern_score = SCORES[lines_cleared][t_spin]
            self.goal -= pattern_score
            pattern_score *= 100 * self.level
            pattern_name = "\n".join(pattern_name)

        if self.combo >= 1:
            combo_score = (20 if lines_cleared == 1 else 50) * self.combo * self.level

        self.score += pattern_score + combo_score

        return pattern_name, pattern_score, self.combo, combo_score


class TetrisLogic:
    """Tetris game logic"""

    # These class attributes can be redefined on inheritance
    AUTOREPEAT_DELAY = AUTOREPEAT_DELAY
    AUTOREPEAT_PERIOD = AUTOREPEAT_PERIOD
    MATRIX_PIECE_COORD = MATRIX_PIECE_COORD

    timer = AbstractScheduler()

    def __init__(self, lines=LINES, collumns=COLLUMNS, nb_next_pieces=NEXT_PIECES):
        """init game with a `lines`x`collumns` size matrix
        and `nb_next_pieces`"""
        self.stats = Stats()
        self.load_high_score()
        self.held = HoldQueue()
        self.matrix = Matrix(lines, collumns)
        self.next = NextQueue(nb_next_pieces)
        self.autorepeatable_actions = (self.move_left, self.move_right, self.soft_drop)
        self.pressed_actions = []

    def new_game(self, level=1):
        """start a new game at `level`"""
        self.stats.new_game(level)

        self.pressed_actions = []

        self.matrix.reset()
        self.next.pieces = [Tetromino() for n in range(self.next.nb_pieces)]
        self.held.piece = None
        self.timer.postpone(self.stats.update_time, 1)

        self.on_new_game(self.matrix, self.next.pieces)
        self.new_level()

    def on_new_game(self, matrix, next_pieces):
        pass

    def new_level(self):
        self.stats.new_level()
        self.on_new_level(self.stats.level)
        self.generation_phase()

    def on_new_level(self, level):
        pass

    # Tetris Engine

    def generation_phase(self, held_piece=None):
        if not held_piece:
            self.matrix.piece = self.next.pieces.pop(0)
            self.next.pieces.append(Tetromino())
        self.matrix.piece.coord = self.MATRIX_PIECE_COORD
        self.matrix.ghost = self.matrix.piece.ghost()
        self.refresh_ghost()

        self.on_generation_phase(
            self.matrix, self.matrix.piece, self.matrix.ghost, self.next.pieces
        )
        self.falling_phase()

    def refresh_ghost(self):
        self.matrix.ghost.coord = self.matrix.piece.coord
        for ghost_mino, current_mino in zip(self.matrix.ghost, self.matrix.piece):
            ghost_mino.coord = current_mino.coord
        while self.matrix.space_to_move(
            self.matrix.ghost.coord + Movement.DOWN,
            (mino.coord for mino in self.matrix.ghost),
        ):
            self.matrix.ghost.coord += Movement.DOWN

    def on_generation_phase(self, matrix, falling_piece, ghost_piece, next_pieces):
        pass

    def falling_phase(self):
        self.timer.cancel(self.lock_phase)
        self.timer.cancel(self.locks_down)
        self.matrix.piece.locked = False
        self.timer.postpone(self.lock_phase, self.stats.fall_delay)
        self.on_falling_phase(self.matrix.piece)

    def on_falling_phase(self, falling_piece):
        pass

    def lock_phase(self):
        self.move(Movement.DOWN)

    def on_locked(self, falling_piece):
        pass

    def move(self, movement, rotated_coords=None, lock=True):
        potential_coord = self.matrix.piece.coord + movement
        potential_minoes_coords = rotated_coords or (
            mino.coord for mino in self.matrix.piece
        )
        if self.matrix.space_to_move(potential_coord, potential_minoes_coords):
            self.matrix.piece.coord = potential_coord
            if rotated_coords:
                for mino, coord in zip(self.matrix.piece, rotated_coords):
                    mino.coord = coord
            self.refresh_ghost()
            if movement != Movement.DOWN:
                self.matrix.piece.rotated_last = False
            if self.matrix.space_to_fall():
                self.falling_phase()
            else:
                self.matrix.piece.locked = True
                self.on_locked(self.matrix.piece)
                self.timer.reset(self.locks_down, self.stats.lock_delay)
            return True
        else:
            return False

    def rotate(self, spin):
        rotated_coords = tuple(mino.coord @ spin for mino in self.matrix.piece)
        for rotation_point, liberty_degree in enumerate(
            self.matrix.piece.SRS[spin][self.matrix.piece.orientation], start=1
        ):
            if self.move(liberty_degree, rotated_coords, lock=False):
                self.matrix.piece.orientation = (
                    self.matrix.piece.orientation + spin
                ) % 4
                self.matrix.piece.rotated_last = True
                if rotation_point == 5:
                    self.matrix.piece.rotation_point_5_used = True
                return True
        else:
            return False

    def locks_down(self):
        # self.timer.cancel(self.repeat_action)
        self.timer.cancel(self.lock_phase)

        # Game over
        if all(
            (mino.coord + self.matrix.piece.coord).y >= self.matrix.lines
            for mino in self.matrix.piece
        ):
            self.game_over()
            return

        for mino in self.matrix.piece:
            coord = mino.coord + self.matrix.piece.coord
            if coord.y <= self.matrix.lines + 3:
                self.matrix[coord.y][coord.x] = mino

        self.on_locks_down(self.matrix, self.matrix.piece)

        # Pattern phase

        # T-Spin
        if type(self.matrix.piece) == T_Tetrimino and self.matrix.piece.rotated_last:
            a = self.is_t_slot(T_Slot.A)
            b = self.is_t_slot(T_Slot.B)
            c = self.is_t_slot(T_Slot.C)
            d = self.is_t_slot(T_Slot.D)
            if a and b and (c or d):
                t_spin = T_Spin.T_SPIN
            elif c and d and (a or b):
                if self.matrix.piece.rotation_point_5_used:
                    t_spin = T_Spin.T_SPIN
                else:
                    t_spin = T_Spin.MINI
            else:
                t_spin = T_Spin.NONE
        else:
            t_spin = T_Spin.NONE

        # Clear complete lines
        self.lines_to_remove = []
        for y, line in reversed(list(enumerate(self.matrix))):
            if all(mino for mino in line):
                self.lines_to_remove.append(y)
        lines_cleared = len(self.lines_to_remove)
        if lines_cleared:
            self.stats.lines_cleared += lines_cleared

        # Animate phase

        self.on_animate_phase(self.matrix, self.lines_to_remove)

        # Eliminate phase
        self.on_eliminate_phase(self.matrix, self.lines_to_remove)
        for y in self.lines_to_remove:
            self.matrix.pop(y)
            self.matrix.append_new_line()

        # Completion phase

        pattern_name, pattern_score, nb_combo, combo_score = self.stats.locks_down(
            t_spin, lines_cleared
        )
        self.on_completion_phase(pattern_name, pattern_score, nb_combo, combo_score)

        if self.stats.goal <= 0:
            self.new_level()
        else:
            self.generation_phase()

    def on_locks_down(self, matrix, falling_piece):
        pass

    def on_animate_phase(self, matrix, lines_to_remove):
        pass

    def on_eliminate_phase(self, matrix, lines_to_remove):
        pass

    def on_completion_phase(self, pattern_name, pattern_score, nb_combo, combo_score):
        pass

    # Actions

    def move_left(self):
        self.move(Movement.LEFT)

    def move_right(self):
        self.move(Movement.RIGHT)

    def rotate_clockwise(self):
        self.rotate(Spin.CLOCKWISE)

    def rotate_counter(self):
        self.rotate(Spin.COUNTER)

    def soft_drop(self):
        moved = self.move(Movement.DOWN)
        if moved:
            self.stats.score += 1
        return moved

    def hard_drop(self):
        self.timer.cancel(self.lock_phase)
        self.timer.cancel(self.locks_down)
        while self.move(Movement.DOWN, lock=False):
            self.stats.score += 2
        self.locks_down()

    def hold(self):
        if not self.matrix.piece.hold_enabled:
            return

        self.matrix.piece.hold_enabled = False
        self.timer.cancel(self.lock_phase)
        self.matrix.piece, self.held.piece = self.held.piece, self.matrix.piece

        for mino, coord in zip(self.held.piece, self.held.piece.MINOES_COORDS):
            mino.coord = coord

        self.on_hold(self.held.piece)
        self.generation_phase(self.matrix.piece)

    def on_hold(self, held_piece):
        pass

    T_SLOT_COORDS = (Coord(-1, 1), Coord(1, 1), Coord(-1, 1), Coord(-1, -1))

    def is_t_slot(self, n):
        t_slot_coord = (
            self.matrix.piece.coord
            + self.T_SLOT_COORDS[(self.matrix.piece.orientation + n) % 4]
        )
        return not self.matrix.cell_is_free(t_slot_coord)

    def pause(self):
        self.stop_all()
        self.pressed_actions = []
        self.timer.cancel(self.repeat_action)
        self.on_pause()

    def on_pause(self):
        pass

    def resume(self):
        self.timer.postpone(self.lock_phase, self.stats.fall_delay)
        if self.matrix.piece.locked:
            self.timer.postpone(self.locks_down, self.stats.lock_delay)
        self.timer.postpone(self.stats.update_time, 1)
        self.on_resume()

    def on_resume(self):
        pass

    def game_over(self):
        self.stop_all()
        self.save_high_score()
        self.on_game_over()

    def on_game_over(self):
        pass

    def stop_all(self):
        self.timer.cancel(self.lock_phase)
        self.timer.cancel(self.locks_down)
        self.timer.cancel(self.stats.update_time)

    def do_action(self, action):
        action()
        if action in self.autorepeatable_actions:
            self.pressed_actions.append(action)
            if action == self.soft_drop:
                delay = self.stats.fall_delay / 20
            else:
                delay = self.AUTOREPEAT_DELAY
            self.timer.reset(self.repeat_action, delay)

    def repeat_action(self):
        if not self.pressed_actions:
            return

        self.pressed_actions[-1]()
        self.timer.postpone(self.repeat_action, self.AUTOREPEAT_PERIOD)

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
