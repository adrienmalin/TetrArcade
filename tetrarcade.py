# -*- coding: utf-8 -*-
import sys
import locale
import time
import os
import itertools

try:
    import arcade
except ImportError:
    sys.exit(
"""This game require arcade library.
You can install it with:
python -m pip install --user arcade
"""
)

from tetrislogic import TetrisLogic, State, AbstractScheduler, NB_LINES


# Constants
# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "TETRARCADE"

# Delays (seconds)
HIGHLIGHT_TEXT_DISPLAY_DELAY = 1

# Text
TEXT_COLOR = arcade.color.BUBBLES
HIGHLIGHT_TEXT_COLOR = arcade.color.BUBBLES
FONT_NAME = "joystix monospace.ttf"
TEXT_MARGIN = 40
FONT_SIZE = 16
TEXT_HEIGHT = 20.8
HIGHLIGHT_TEXT_FONT_SIZE = 20
TITLE_AND_CONTROL_TEXT = """TETRARCADE

CONTROLS
MOVE LEFT            ←
MOVE RIGHT           →
SOFT DROP            ↓
HARD DROP        SPACE
ROTATE CLOCKWISE     ↑
ROTATE COUNTER       Z
HOLD                 C
PAUSE              ESC"""
START_TEXT = TITLE_AND_CONTROL_TEXT + "\n\nPRESS [ENTER] TO START"
PAUSE_TEXT = TITLE_AND_CONTROL_TEXT + "\n\nPRESS [ESC] TO RESUME"
STATS_TEXT = """SCORE

HIGH SCORE

LEVEL

GOAL

LINES

TIME
"""
GAME_OVER_TEXT = """GAME
OVER

PRESS
[ENTER]
TO PLAY
AGAIN"""

# Paths
WINDOW_BG = "images/bg.jpg"
MATRIX_SPRITE_PATH = "images/matrix.png"
MINOES_SPRITES_PATHS = {
    "orange":  "images/orange_mino.png",
    "blue":    "images/blue_mino.png",
    "yellow":  "images/yellow_mino.png",
    "cyan":    "images/cyan_mino.png",
    "green":   "images/green_mino.png",
    "red":     "images/red_mino.png",
    "magenta": "images/magenta_mino.png"
}
if sys.platform == "win32":
    USER_PROFILE_DIR = os.environ.get("appdata", os.path.expanduser("~\Appdata\Roaming"))
else:
    USER_PROFILE_DIR = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
USER_PROFILE_DIR = os.path.join(USER_PROFILE_DIR, "TetrArcade")
HIGH_SCORE_PATH = os.path.join(USER_PROFILE_DIR, ".high_score")

# Transparency (0=invisible, 255=opaque)
NORMAL_ALPHA = 200
PRELOCKED_ALPHA = 127
GHOST_ALPHA = 50
MATRIX_SRITE_ALPHA = 100


class ArcadeScheduler(AbstractScheduler):

    def __init__(self):
        self._tasks = {}

    def start(self, task, period):
        _task = lambda _: task()
        self._tasks[task] = _task
        arcade.schedule(_task, period)

    def stop(self, task):
        try:
            _task = self._tasks[task]
        except KeyError:
            pass
        else:
            arcade.unschedule(_task)
            del self._tasks[task]

    def restart(self, task, period):
        try:
            _task = self._tasks[task]
        except KeyError:
            _task = lambda _: task()
            self._tasks[task] = _task
        else:
            arcade.unschedule(_task)
        arcade.schedule(_task, period)


class TetrArcade(TetrisLogic, arcade.Window):

    scheduler = ArcadeScheduler()

    def __init__(self):
        super().__init__()

        locale.setlocale(locale.LC_ALL, '')

        self.KEY_MAP = {
            State.STARTING: {
                arcade.key.ENTER:     self.new_game
            },
            State.PLAYING: {
                arcade.key.LEFT:      self.move_left,
                arcade.key.NUM_4:     self.move_left,
                arcade.key.RIGHT:     self.move_right,
                arcade.key.NUM_6:     self.move_right,
                arcade.key.SPACE:     self.hard_drop,
                arcade.key.NUM_8:     self.hard_drop,
                arcade.key.DOWN:      self.soft_drop,
                arcade.key.NUM_2:     self.soft_drop,
                arcade.key.UP:        self.rotate_clockwise,
                arcade.key.X:         self.rotate_clockwise,
                arcade.key.NUM_1:     self.rotate_clockwise,
                arcade.key.NUM_5:     self.rotate_clockwise,
                arcade.key.NUM_9:     self.rotate_clockwise,
                arcade.key.Z:         self.rotate_counterclockwise,
                arcade.key.NUM_3:     self.rotate_counterclockwise,
                arcade.key.NUM_7:     self.rotate_counterclockwise,
                arcade.key.C:         self.swap,
                arcade.key.MOD_SHIFT: self.swap,
                arcade.key.NUM_0:     self.swap,
                arcade.key.ESCAPE:    self.pause,
                arcade.key.F1:        self.pause,
            },
            State.PAUSED: {
                arcade.key.ESCAPE:    self.resume,
                arcade.key.F1:        self.resume
            },
            State.OVER: {
                arcade.key.ENTER:     self.new_game
            }
        }

        self.highlight_texts = []

        arcade.Window.__init__(
            self,
            width = WINDOW_WIDTH,
            height = WINDOW_HEIGHT,
            title = WINDOW_TITLE,
            resizable = False,
            antialiasing = False
        )

        center_x = self.width / 2
        center_y = self.height / 2
        self.bg_sprite = arcade.Sprite(WINDOW_BG)
        self.bg_sprite.center_x = center_x
        self.bg_sprite.center_y = center_y
        self.matrix_minoes_sprites = []
        self.held_piece_sprites = arcade.SpriteList()
        self.current_piece_sprites = arcade.SpriteList()
        self.ghost_piece_sprites = arcade.SpriteList()
        self.next_pieces_sprites = arcade.SpriteList()
        self.matrix_sprite = arcade.Sprite(MATRIX_SPRITE_PATH)
        self.matrix_sprite.alpha = MATRIX_SRITE_ALPHA
        self.matrix_sprite.center_x = center_x
        self.matrix_sprite.center_y = center_y
        self.matrix_sprite.left = int(self.matrix_sprite.left)
        self.matrix_sprite.top = int(self.matrix_sprite.top)
        self.general_text = arcade.create_text(
            text = STATS_TEXT,
            color = TEXT_COLOR,
            font_size = FONT_SIZE,
            font_name = FONT_NAME,
            anchor_x = 'right'
        )

    def new_game(self):
        self.highlight_texts = []
        self.matrix_minoes_sprites = []
        super().new_game()

    def new_current_piece(self):
        super().new_current_piece()
        self.reload_next_pieces()
        self.reload_current_piece()

    def lock(self):
        super().lock()

    def enter_the_matrix(self):
        super().enter_the_matrix()
        self.update_current_piece()
        for mino_coord, mino_sprite in zip(
            self.current_piece.minoes_coords,
            self.current_piece_sprites
        ):
            mino_coord += self.current_piece.coord
            self.matrix_minoes_sprites[
                mino_coord.y
            ].append(mino_sprite)

    def append_new_line_to_matrix(self):
        super().append_new_line_to_matrix()
        self.matrix_minoes_sprites.append(arcade.SpriteList())

    def remove_line_of_matrix(self, line):
        super().remove_line_of_matrix(line)
        self.matrix_minoes_sprites.pop(line)
        for line_sprites in self.matrix_minoes_sprites[line:NB_LINES+2]:
            for mino_sprite in line_sprites:
                mino_sprite.center_y -= mino_sprite.height-1

    def swap(self):
        super().swap()
        self.reload_held_piece()
        self.reload_current_piece()

    def game_over(self):
        super().game_over()

    def on_key_press(self, key, modifiers):
        for key_or_modifier in (key, modifiers):
            try:
                action = self.KEY_MAP[self.state][key_or_modifier]
            except KeyError:
                pass
            else:
                self.do_action(action)

    def on_key_release(self, key, modifiers):
        try:
            action = self.KEY_MAP[self.state][key]
        except KeyError:
            pass
        else:
            self.remove_action(action)

    def show_text(self, text):
        self.highlight_texts.append(text)
        self.scheduler.restart(self.del_highlight_text, HIGHLIGHT_TEXT_DISPLAY_DELAY)

    def del_highlight_text(self):
        if self.highlight_texts:
            self.highlight_texts.pop(0)
        else:
            self.scheduler.stop(self.del_highlight_text)

    def reload_piece(self, piece):
        piece_sprites = arcade.SpriteList()
        for mino_coord in piece.minoes_coords:
            mino_sprite_path = MINOES_SPRITES_PATHS[piece.MINOES_COLOR]
            mino_sprite = arcade.Sprite(mino_sprite_path)
            mino_sprite.alpha = NORMAL_ALPHA
            piece_sprites.append(mino_sprite)
        return piece_sprites

    def reload_held_piece(self):
        self.held_piece_sprites = self.reload_piece(self.held_piece)

    def reload_next_pieces(self):
        self.next_pieces_sprites = arcade.SpriteList()
        for piece in self.next_pieces:
            for mino_coord in piece.minoes_coords:
                mino_sprite_path = MINOES_SPRITES_PATHS[piece.MINOES_COLOR]
                mino_sprite = arcade.Sprite(mino_sprite_path)
                mino_sprite.alpha = NORMAL_ALPHA
                self.next_pieces_sprites.append(mino_sprite)

    def reload_current_piece(self):
        self.current_piece_sprites = self.reload_piece(self.current_piece)
        self.ghost_piece_sprites = self.reload_piece(self.ghost_piece)

    def update_piece(self, piece, piece_sprites):
        if piece:
            for mino_sprite, mino_coord in zip(
                piece_sprites, piece.minoes_coords
            ):
                mino_coord += piece.coord
                mino_sprite.left = self.matrix_sprite.left + mino_coord.x*(mino_sprite.width-1)
                mino_sprite.bottom = self.matrix_sprite.bottom + mino_coord.y*(mino_sprite.height-1)

    def update_current_piece(self):
        self.update_piece(self.current_piece, self.current_piece_sprites)
        if self.current_piece.prelocked:
            alpha = (
                PRELOCKED_ALPHA
                if self.current_piece.prelocked
                else NORMAL_ALPHA
            )
            for mino_sprite in self.current_piece_sprites:
                mino_sprite.alpha = alpha

    def on_draw(self):
        arcade.start_render()
        self.bg_sprite.draw()

        if self.state in (State.PLAYING, State.OVER):
            self.matrix_sprite.draw()
            for line in self.matrix_minoes_sprites:
                line.draw()

            self.update_piece(self.held_piece, self.held_piece_sprites)
            self.held_piece_sprites.draw()

            self.update_current_piece()
            self.current_piece_sprites.draw()

            self.update_piece(self.ghost_piece, self.ghost_piece_sprites)
            for mino_sprite in self.ghost_piece_sprites:
                mino_sprite.alpha = GHOST_ALPHA
            self.ghost_piece_sprites.draw()

            for n, piece in enumerate(self.next_pieces):
                for mino_sprite, mino_coord in zip(
                    self.next_pieces_sprites[4*n:4*(n+1)], piece.minoes_coords
                ):
                    mino_coord += piece.coord
                    mino_sprite.left = self.matrix_sprite.left + mino_coord.x*(mino_sprite.width-1)
                    mino_sprite.bottom = self.matrix_sprite.bottom + mino_coord.y*(mino_sprite.height-1)
            self.next_pieces_sprites.draw()

            arcade.render_text(
                self.general_text,
                self.matrix_sprite.left - TEXT_MARGIN,
                self.matrix_sprite.bottom
            )
            t = time.localtime(self.time)
            for y, text in enumerate(
                (

                    "{:02d}:{:02d}:{:02d}".format(
                        t.tm_hour-1, t.tm_min, t.tm_sec
                    ),
                    "{:n}".format(self.nb_lines),
                    "{:n}".format(self.goal),
                    "{:n}".format(self.level),
                    "{:n}".format(self.high_score),
                    "{:n}".format(self.score)
                )
            ):
                arcade.draw_text(
                    text = text,
                    start_x = self.matrix_sprite.left - TEXT_MARGIN,
                    start_y = self.matrix_sprite.bottom + 2*y*TEXT_HEIGHT,
                    color = TEXT_COLOR,
                    font_size = FONT_SIZE,
                    align = 'right',
                    font_name = FONT_NAME,
                    anchor_x = 'right'
                )

        highlight_text = {
            State.STARTING: START_TEXT,
            State.PLAYING: self.highlight_texts[0] if self.highlight_texts else "",
            State.PAUSED: PAUSE_TEXT,
            State.OVER: GAME_OVER_TEXT
        }.get(self.state, "")
        if highlight_text:
            arcade.draw_text(
                text = highlight_text,
                start_x = self.matrix_sprite.center_x,
                start_y = self.matrix_sprite.center_y,
                color = HIGHLIGHT_TEXT_COLOR,
                font_size = HIGHLIGHT_TEXT_FONT_SIZE,
                align = 'center',
                font_name = FONT_NAME,
                anchor_x = 'center',
                anchor_y = 'center'
            )

    def load_high_score(self):
        try:
            with open(HIGH_SCORE_PATH, "r") as f:
               self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        try:
            if not os.path.exists(USER_PROFILE_DIR):
                os.makedirs(USER_PROFILE_DIR)
            with open(HIGH_SCORE_PATH, mode='w') as f:
                f.write(str(self.high_score))
        except Exception as e:
            sys.exit(
                """High score: {:n}
High score could not be saved:
""".format(self.high_score)
                + str(e)
            )


def main():
    tetrarcade = TetrArcade()
    arcade.run()
    tetrarcade.save_high_score()

if __name__ == "__main__":
    main()
