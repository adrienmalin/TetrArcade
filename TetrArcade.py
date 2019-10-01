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
BG_COLOR = (7, 11, 21)

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
FONT_NAME = "joystix monospace.ttf"
STATS_TEXT_MARGIN = 40
STATS_TEXT_SIZE = 16
HIGHLIGHT_TEXT_COLOR = arcade.color.BUBBLES
HIGHLIGHT_TEXT_SIZE = 20

CONTROL_TEXT = """


CONTROLS

MOVE LEFT            ←
MOVE RIGHT           →
SOFT DROP            ↓
HARD DROP        SPACE
ROTATE CLOCKWISE     ↑
ROTATE COUNTER       Z
HOLD                 C
FULLSCREEN         F11
PAUSE              ESC
QUIT            ALT+F4


"""
START_TEXT = "TETRARCADE" + CONTROL_TEXT + "PRESS [ENTER] TO START"
PAUSE_TEXT = "PAUSE" + CONTROL_TEXT + "PRESS [ESC] TO RESUME"
GAME_OVER_TEXT = """GAME
OVER

PRESS
[ENTER]
TO PLAY
AGAIN"""


class MinoSprite(arcade.Sprite):

    def __init__(self, mino, window, alpha):
        super().__init__(MINOES_SPRITES_PATHS[mino.color], window.scale)
        self.alpha = alpha
        self.window = window

    def set_position(self, x, y):
        size = MINO_SIZE * self.scale
        self.left   = self.window.matrix_bg.left   + x*size
        self.bottom = self.window.matrix_bg.bottom + y*size


class MinoesSprites(arcade.SpriteList):

    def resize(self, scale):
        for sprite in self:
            sprite.scale = scale
        self.refresh()


class TetrominoSprites(MinoesSprites):

    def __init__(self, tetromino, window, alpha=NORMAL_ALPHA):
        super().__init__()
        self.tetromino = tetromino
        for mino in tetromino:
            mino.sprite = MinoSprite(mino, window, alpha)
            self.append(mino.sprite)

    def refresh(self):
        for mino in self.tetromino:
            coord = mino.coord + self.tetromino.coord
            mino.sprite.set_position(coord.x, coord.y)

    def set_alpha(self, alpha):
        for sprite in self:
            sprite.alpha = alpha


class MatrixSprites(MinoesSprites):

    def __init__(self, matrix):
        super().__init__()
        self.matrix = matrix
        self.refresh()

    def refresh(self):
        for y, line in enumerate(self.matrix):
            for x, mino in enumerate(line):
                if mino:
                    mino.sprite.set_position(x, y)
                    self.append(mino.sprite)


class TetrArcade(tetrislogic.TetrisLogic, arcade.Window):

    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.highlight_texts = []
        self.tasks = {}

        self.KEY_MAP = {
            tetrislogic.State.STARTING: {
                arcade.key.ENTER:     self.new_game,
                arcade.key.F11:       self.toogle_fullscreen
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
                arcade.key.F11:       self.toogle_fullscreen
            },
            tetrislogic.State.PAUSED: {
                arcade.key.ESCAPE:    self.resume,
                arcade.key.F1:        self.resume,
                arcade.key.F11:       self.toogle_fullscreen
            },
            tetrislogic.State.OVER: {
                arcade.key.ENTER:     self.new_game,
                arcade.key.F11:       self.toogle_fullscreen
            }
        }

        super().__init__()

        arcade.Window.__init__(
            self,
            width = WINDOW_WIDTH,
            height = WINDOW_HEIGHT,
            title = WINDOW_TITLE,
            resizable = True,
            antialiasing = False
        )
        arcade.set_background_color(BG_COLOR)
        self.bg = arcade.Sprite(WINDOW_BG_PATH)
        self.matrix_bg = arcade.Sprite(MATRIX_SPRITE_PATH)
        self.matrix_bg.alpha = MATRIX_BG_ALPHA
        self.matrix.sprites = MatrixSprites(self.matrix)

    def on_hide(self):
        self.pause()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        center_x = width / 2
        center_y = height / 2
        self.scale = min(width/WINDOW_WIDTH, height/WINDOW_HEIGHT)

        self.bg.scale = max(width/WINDOW_WIDTH, height/WINDOW_HEIGHT)
        self.bg.center_x = center_x
        self.bg.center_y = center_y

        self.matrix_bg.scale = self.scale
        self.matrix_bg.center_x = center_x
        self.matrix_bg.center_y = center_y
        self.matrix_bg.left = int(self.matrix_bg.left)
        self.matrix_bg.top  = int(self.matrix_bg.top)

        self.matrix.sprites.resize(self.scale)

        for tetromino in [self.held, self.current, self.ghost] + self.next:
            if tetromino:
                tetromino.sprites.resize(self.scale)

    def toogle_fullscreen(self):
        self.fullscreen = not self.fullscreen

    def new_game(self):
        self.highlight_texts = []
        super().new_game()

    def new_tetromino(self):
        tetromino = super().new_tetromino()
        tetromino.sprites = TetrominoSprites(tetromino, self)
        return tetromino

    def new_current(self):
        self.matrix.sprites = MatrixSprites(self.matrix)
        super().new_current()
        self.ghost.sprites = TetrominoSprites(self.ghost, self, GHOST_ALPHA)
        for tetromino in [self.current, self.ghost] + self.next:
            tetromino.sprites.refresh()

    def move(self, movement, prelock=True):
        moved = super().move(movement, prelock)
        if self.current.prelocked:
            self.current.sprites.set_alpha(PRELOCKED_ALPHA)
        if moved:
            size = MINO_SIZE * self.scale
            change_x = movement.x * size
            change_y = movement.y * size
            self.current.sprites.move(change_x, change_y)
            if movement in (tetrislogic.Movement.LEFT, tetrislogic.Movement.RIGHT):
                self.ghost.sprites.refresh()
        return moved

    def rotate(self, rotation):
        rotated = super().rotate(rotation)
        if rotated:
            for tetromino in (self.current, self.ghost):
                tetromino.sprites.refresh()
        return rotated

    def swap(self):
        super().swap()
        self.ghost.sprites = TetrominoSprites(self.ghost, self, GHOST_ALPHA)
        for tetromino in [self.held, self.current, self.ghost]:
            if tetromino:
                tetromino.sprites.refresh()

    def lock(self):
        self.current.sprites.refresh()
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

            t = time.localtime(self.time)
            font_size = STATS_TEXT_SIZE * self.scale
            for y, text in enumerate(
                (
                    "TIME",
                    "LINES",
                    "GOAL",
                    "LEVEL",
                    "HIGH SCORE",
                    "SCORE"
                )
            ):
                arcade.draw_text(
                    text = text,
                    start_x = self.matrix_bg.left - STATS_TEXT_MARGIN*self.scale - self.matrix_bg.width,
                    start_y = self.matrix_bg.bottom + 1.5*(2*y+1)*font_size,
                    color = TEXT_COLOR,
                    font_size = font_size,
                    align = 'right',
                    font_name = FONT_NAME,
                    anchor_x = 'left'
                )
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
                    start_x = self.matrix_bg.left - STATS_TEXT_MARGIN*self.scale,
                    start_y = self.matrix_bg.bottom + 3*y*font_size,
                    color = TEXT_COLOR,
                    font_size = font_size,
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
                font_size = HIGHLIGHT_TEXT_SIZE * self.scale,
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
