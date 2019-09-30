# -*- coding: utf-8 -*-
import sys
import locale
import time
import os

try:
    import arcade
except ImportError:
    sys.exit(
        """This game require arcade library.
You can install it with:
python -m pip install --user arcade"""
    )

import tetrislogic


# Constants
# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "TETRARCADE"
MINO_SIZE = 20

# Delays (seconds)
HIGHLIGHT_TEXT_DISPLAY_DELAY = 0.7

# Transparency (0=invisible, 255=opaque)
NORMAL_ALPHA = 200
PRELOCKED_ALPHA = 100
GHOST_ALPHA = 30
MATRIX_BG_ALPHA = 100

# Sprites
WINDOW_BG_PATH = "images/bg.jpg"
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

# User profile path
if sys.platform == "win32":
    USER_PROFILE_DIR = os.environ.get("appdata", os.path.expanduser("~\Appdata\Roaming"))
else:
    USER_PROFILE_DIR = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
USER_PROFILE_DIR = os.path.join(USER_PROFILE_DIR, "TetrArcade")
HIGH_SCORE_PATH = os.path.join(USER_PROFILE_DIR, ".high_score")

# Text
TEXT_COLOR = arcade.color.BUBBLES
HIGHLIGHT_TEXT_COLOR = arcade.color.BUBBLES
FONT_NAME = "joystix monospace.ttf"
TEXT_MARGIN = 40
FONT_SIZE = 16
TEXT_HEIGHT = 20.8
HIGHLIGHT_TEXT_FONT_SIZE = 20

CONTROL_TEXT = """


CONTROLS

MOVE LEFT            ←
MOVE RIGHT           →
SOFT DROP            ↓
HARD DROP        SPACE
ROTATE CLOCKWISE     ↑
ROTATE COUNTER       Z
HOLD                 C
PAUSE              ESC


"""
START_TEXT = "TETRARCADE" + CONTROL_TEXT + "PRESS [ENTER] TO START"
PAUSE_TEXT = "PAUSE" + CONTROL_TEXT + "PRESS [ESC] TO RESUME"
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


class MinoSprite(arcade.Sprite):

    def __init__(self, mino, matrix_bg, alpha):
        super().__init__(MINOES_SPRITES_PATHS[mino.color])
        self.alpha = alpha
        self.matrix_bg = matrix_bg

    def set_position(self, x, y):
        self.left   = self.matrix_bg.left   + x*MINO_SIZE
        self.bottom = self.matrix_bg.bottom + y*MINO_SIZE


class TetrominoSprites(arcade.SpriteList):

    def __init__(self, tetromino, matrix_bg, alpha=NORMAL_ALPHA):
        super().__init__()
        self.tetromino = tetromino
        self.matrix_bg = matrix_bg
        for mino in tetromino:
            mino.sprite = MinoSprite(mino, matrix_bg, alpha)
            self.append(mino.sprite)

    def update(self):
        for mino in self.tetromino:
            coord = mino.coord + self.tetromino.coord
            mino.sprite.set_position(coord.x, coord.y)
        super().update()

    def set_alpha(self, alpha):
        for sprite in self:
            sprite.alpha = alpha


class MatrixSprites(arcade.SpriteList):

    def __init__(self, matrix):
        super().__init__()
        self.matrix = matrix
        self.update()

    def update(self):
        for y, line in enumerate(self.matrix):
            for x, mino in enumerate(line):
                if mino:
                    mino.sprite.set_position(x, y)
                    self.append(mino.sprite)
        super().update()


class TetrArcade(tetrislogic.TetrisLogic, arcade.Window):

    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.highlight_texts = []
        self.tasks = {}

        self.KEY_MAP = {
            tetrislogic.State.STARTING: {
                arcade.key.ENTER:     self.new_game
            },
            tetrislogic.State.PLAYING: {
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
                arcade.key.Z:         self.rotate_counter,
                arcade.key.NUM_3:     self.rotate_counter,
                arcade.key.NUM_7:     self.rotate_counter,
                arcade.key.C:         self.swap,
                arcade.key.MOD_SHIFT: self.swap,
                arcade.key.NUM_0:     self.swap,
                arcade.key.ESCAPE:    self.pause,
                arcade.key.F1:        self.pause,
            },
            tetrislogic.State.PAUSED: {
                arcade.key.ESCAPE:    self.resume,
                arcade.key.F1:        self.resume
            },
            tetrislogic.State.OVER: {
                arcade.key.ENTER:     self.new_game
            }
        }

        super().__init__()

        arcade.Window.__init__(
            self,
            width = WINDOW_WIDTH,
            height = WINDOW_HEIGHT,
            title = WINDOW_TITLE,
            resizable = False,
            antialiasing = False
        )

        center_x = WINDOW_WIDTH / 2
        center_y = WINDOW_HEIGHT / 2
        self.bg = arcade.Sprite(WINDOW_BG_PATH)
        self.bg.center_x = center_x
        self.bg.center_y = center_y
        self.matrix_bg = arcade.Sprite(MATRIX_SPRITE_PATH)
        self.matrix_bg.alpha = MATRIX_BG_ALPHA
        self.matrix_bg.center_x = center_x
        self.matrix_bg.center_y = center_y
        self.matrix_bg.left = int(self.matrix_bg.left)
        self.matrix_bg.top  = int(self.matrix_bg.top)
        self.matrix.sprites = MatrixSprites(self.matrix)
        self.stats_text = arcade.create_text(
            text = STATS_TEXT,
            color = TEXT_COLOR,
            font_size = FONT_SIZE,
            font_name = FONT_NAME,
            anchor_x = 'right'
        )

    def new_game(self):
        self.highlight_texts = []
        super().new_game()

    def new_tetromino(self):
        tetromino = super().new_tetromino()
        tetromino.sprites = TetrominoSprites(tetromino, self.matrix_bg)
        return tetromino

    def new_current(self):
        self.matrix.sprites = MatrixSprites(self.matrix)
        super().new_current()
        self.ghost.sprites = TetrominoSprites(self.ghost, self.matrix_bg, GHOST_ALPHA)
        for tetromino in [self.current, self.ghost] + self.next:
            tetromino.sprites.update()

    def move(self, movement, prelock=True):
        moved = super().move(movement, prelock)
        if self.current.prelocked:
            self.current.sprites.set_alpha(PRELOCKED_ALPHA)
        if moved:
            change_x = movement.x * MINO_SIZE
            change_y = movement.y * MINO_SIZE
            self.current.sprites.move(change_x, change_y)
            if movement in (tetrislogic.Movement.LEFT, tetrislogic.Movement.RIGHT):
                self.ghost.sprites.update()
        return moved

    def rotate(self, rotation):
        rotated = super().rotate(rotation)
        if rotated:
            for tetromino in (self.current, self.ghost):
                tetromino.sprites.update()
        return rotated

    def swap(self):
        super().swap()
        self.ghost = TetrominoSprites(self.ghost, self.matrix_bg, GHOST_ALPHA)
        for tetromino in [self.held, self.current, self.ghost]:
            if tetromino:
                tetromino.sprites.update()

    def lock(self):
        self.current.sprites.update()
        super().lock()

    def on_key_press(self, key, modifiers):
        for key_or_modifier in (key, modifiers):
            try:
                action = self.KEY_MAP[self.state][key_or_modifier]
            except KeyError:
                pass
            else:
                self.do_action(action)

    def on_key_release(self, key, modifiers):
        for key_or_modifier in (key, modifiers):
            try:
                action = self.KEY_MAP[self.state][key_or_modifier]
            except KeyError:
                pass
            else:
                self.remove_action(action)

    def show_text(self, text):
        self.highlight_texts.append(text)
        self.restart(self.del_highlight_text, HIGHLIGHT_TEXT_DISPLAY_DELAY)

    def del_highlight_text(self):
        if self.highlight_texts:
            self.highlight_texts.pop(0)
        else:
            self.stop(self.del_highlight_text)

    def on_draw(self):
        arcade.start_render()
        self.bg.draw()

        if self.state in (tetrislogic.State.PLAYING, tetrislogic.State.OVER):
            self.matrix_bg.draw()
            self.matrix.sprites.draw()

            for tetromino in [self.held, self.current, self.ghost] + self.next:
                if tetromino:
                    tetromino.sprites.draw()

            arcade.render_text(
                self.stats_text,
                self.matrix_bg.left - TEXT_MARGIN,
                self.matrix_bg.bottom
            )
            t = time.localtime(self.time)
            for y, text in enumerate(
                (

                    "{:02d}:{:02d}:{:02d}".format(
                        t.tm_hour-1, t.tm_min, t.tm_sec
                    ),
                    "{:n}".format(self.nb_lines_cleared),
                    "{:n}".format(self.goal),
                    "{:n}".format(self.level),
                    "{:n}".format(self.high_score),
                    "{:n}".format(self.score)
                )
            ):
                arcade.draw_text(
                    text = text,
                    start_x = self.matrix_bg.left - TEXT_MARGIN,
                    start_y = self.matrix_bg.bottom + 2*y*TEXT_HEIGHT,
                    color = TEXT_COLOR,
                    font_size = FONT_SIZE,
                    align = 'right',
                    font_name = FONT_NAME,
                    anchor_x = 'right'
                )

        highlight_text = {
            tetrislogic.State.STARTING: START_TEXT,
            tetrislogic.State.PLAYING: self.highlight_texts[0] if self.highlight_texts else "",
            tetrislogic.State.PAUSED: PAUSE_TEXT,
            tetrislogic.State.OVER: GAME_OVER_TEXT
        }.get(self.state, "")
        if highlight_text:
            arcade.draw_text(
                text = highlight_text,
                start_x = self.matrix_bg.center_x,
                start_y = self.matrix_bg.center_y,
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

    def start(self, task, period):
        _task = lambda _: task()
        self.tasks[task] = _task
        arcade.schedule(_task, period)

    def stop(self, task):
        try:
            _task = self.tasks[task]
        except KeyError:
            pass
        else:
            arcade.unschedule(_task)
            del self.tasks[task]

    def restart(self, task, period):
        try:
            _task = self.tasks[task]
        except KeyError:
            _task = lambda _: task()
            self.tasks[task] = _task
        else:
            arcade.unschedule(_task)
        arcade.schedule(_task, period)


def main():
    tetrarcade = TetrArcade()
    arcade.run()
    tetrarcade.save_high_score()

if __name__ == "__main__":
    main()
