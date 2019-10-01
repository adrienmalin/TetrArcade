# -*- coding: utf-8 -*-
import sys
import locale
import time
import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

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
WINDOW_MIN_WIDTH = 517
WINDOW_MIN_HEIGHT = 388
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
CONF_PATH = os.path.join(USER_PROFILE_DIR, "TetrArcade.ini")

# Text
TEXT_COLOR = arcade.color.BUBBLES
FONT_NAME = "joystix monospace.ttf"
STATS_TEXT_MARGIN = 40
STATS_TEXT_SIZE = 16
HIGHLIGHT_TEXT_COLOR = arcade.color.BUBBLES
HIGHLIGHT_TEXT_SIZE = 20


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
        self.alpha = alpha
        for mino in tetromino:
            mino.sprite = MinoSprite(mino, window, alpha)
            self.append(mino.sprite)

    def refresh(self):
        if self.tetromino.prelocked:
            alpha = PRELOCKED_ALPHA
        else:
            alpha = self.alpha
        for mino in self.tetromino:
            coord = mino.coord + self.tetromino.coord
            mino.sprite.set_position(coord.x, coord.y)
            mino.sprite.alpha = alpha


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

        self.conf = configparser.ConfigParser()
        if self.conf.read(CONF_PATH):
            try:
                self.load_conf()
            except:
                self.new_conf()
                self.load_conf()
        else:
            self.new_conf()
            self.load_conf()

        super().__init__()
        arcade.Window.__init__(
            self,
            width = self.init_width,
            height = self.init_height,
            title = WINDOW_TITLE,
            resizable = True,
            antialiasing = False,
            fullscreen = self.init_fullscreen
        )
        arcade.set_background_color(BG_COLOR)
        self.set_minimum_size(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.bg = arcade.Sprite(WINDOW_BG_PATH)
        self.matrix_bg = arcade.Sprite(MATRIX_SPRITE_PATH)
        self.matrix_bg.alpha = MATRIX_BG_ALPHA
        self.matrix.sprites = MatrixSprites(self.matrix)
        self.on_resize(self.init_width, self.init_height)

    def new_conf(self):
        self.conf["WINDOW"] = {
            "width": WINDOW_WIDTH,
            "height": WINDOW_HEIGHT,
            "fullscreen": False
        }
        self.conf["KEYBOARD"] = {
            "start": "ENTER",
            "move left": "LEFT",
            "move right": "RIGHT",
            "soft drop": "DOWN",
            "hard drop": "SPACE",
            "rotate clockwise": "UP",
            "rotate counter": "Z",
            "hold": "C",
            "pause": "ESCAPE",
            "fullscreen": "F11"
        }
        self.load_conf()
        if not os.path.exists(USER_PROFILE_DIR):
            os.makedirs(USER_PROFILE_DIR)
        with open(CONF_PATH, 'w') as f:
            self.conf.write(f)

    def load_conf(self):
        self.init_width = int(self.conf["WINDOW"]["width"])
        self.init_height = int(self.conf["WINDOW"]["height"])
        self.init_fullscreen = self.conf["WINDOW"].getboolean("fullscreen")

        self.key_map = {
            tetrislogic.State.STARTING: {
                getattr(arcade.key, self.conf["KEYBOARD"]["start"]): self.new_game,
                getattr(arcade.key, self.conf["KEYBOARD"]["fullscreen"]): self.toggle_fullscreen
            },
            tetrislogic.State.PLAYING: {
                getattr(arcade.key, self.conf["KEYBOARD"]["move left"]): self.move_left,
                getattr(arcade.key, self.conf["KEYBOARD"]["move right"]): self.move_right,
                getattr(arcade.key, self.conf["KEYBOARD"]["soft drop"]): self.soft_drop,
                getattr(arcade.key, self.conf["KEYBOARD"]["hard drop"]): self.hard_drop,
                getattr(arcade.key, self.conf["KEYBOARD"]["rotate clockwise"]): self.rotate_clockwise,
                getattr(arcade.key, self.conf["KEYBOARD"]["rotate counter"]): self.rotate_counter,
                getattr(arcade.key, self.conf["KEYBOARD"]["hold"]): self.swap,
                getattr(arcade.key, self.conf["KEYBOARD"]["pause"]): self.pause,
                getattr(arcade.key, self.conf["KEYBOARD"]["fullscreen"]): self.toggle_fullscreen
            },
            tetrislogic.State.PAUSED: {
                getattr(arcade.key, self.conf["KEYBOARD"]["pause"]): self.resume,
                getattr(arcade.key, self.conf["KEYBOARD"]["fullscreen"]): self.toggle_fullscreen
            },
            tetrislogic.State.OVER: {
                getattr(arcade.key, self.conf["KEYBOARD"]["start"]): self.new_game,
                getattr(arcade.key, self.conf["KEYBOARD"]["fullscreen"]): self.toggle_fullscreen
            }
        }

        controls_text = "\n\n\nCONTROLS\n\n" + "\n".join(
            "{:<16s}{:>6s}".format(key, action)
            for key, action in tuple(self.conf["KEYBOARD"].items()) + (("QUIT", "ALT+F4"),)
        ) + "\n\n\n"
        self.start_text = "TETRARCADE" + controls_text + "PRESS [{}] TO START".format(
            self.conf["KEYBOARD"]["start"]
        )
        self.pause_text = "PAUSE" + controls_text + "PRESS [{}] TO RESUME".format(
            self.conf["KEYBOARD"]["pause"]
        )
        self.game_over_text = """GAME
OVER

PRESS
[{}]
TO PLAY
AGAIN""".format(
            self.conf["KEYBOARD"]["start"]
        )

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
        self.current.sprites.refresh()
        if moved:
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
        self.current.prelocked = False
        self.current.sprites.refresh()
        super().lock()

    def on_key_press(self, key, modifiers):
        for key_or_modifier in (key, modifiers):
            try:
                action = self.key_map[self.state][key_or_modifier]
            except KeyError:
                pass
            else:
                self.do_action(action)

    def on_key_release(self, key, modifiers):
        for key_or_modifier in (key, modifiers):
            try:
                action = self.key_map[self.state][key_or_modifier]
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
            tetrislogic.State.STARTING: self.start_text,
            tetrislogic.State.PLAYING: self.highlight_texts[0] if self.highlight_texts else "",
            tetrislogic.State.PAUSED: self.pause_text,
            tetrislogic.State.OVER: self.game_over_text
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

    def on_hide(self):
        self.pause()

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)

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

    def load_high_score(self):
        try:
            with open(HIGH_SCORE_PATH, "rb") as f:
                crypted_high_score = f.read()
                super().load_high_score(crypted_high_score)
        except:
            self.high_score = 0

    def save_high_score(self):
        try:
            if not os.path.exists(USER_PROFILE_DIR):
                os.makedirs(USER_PROFILE_DIR)
            with open(HIGH_SCORE_PATH, mode='wb') as f:
                crypted_high_score = super().save_high_score()
                f.write(crypted_high_score)
        except Exception as e:
            sys.exit(
                """High score: {:n}
High score could not be saved:
""".format(self.high_score) + str(e)
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

    def on_close(self):
        self.save_high_score()
        super().on_close()

def main():
    TetrArcade()
    arcade.run()

if __name__ == "__main__":
    main()
