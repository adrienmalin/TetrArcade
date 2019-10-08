# -*- coding: utf-8 -*-
"""Tetris clone with arcade GUI library"""


import sys
import random

try:
    import arcade
except ImportError as e:
    sys.exit(
        str(e)
        + """
This game require arcade library.
You can install it with:
python -m pip install --user arcade"""
    )
import pyglet

import locale
import time
import os
import itertools
import configparser

from tetrislogic import (
    TetrisLogic,
    Color,
    Coord,
    I_Tetrimino,
    Movement,
    AbstractScheduler,
)


# Constants
# Matrix
LINES = 20
COLLUMNS = 10
NEXT_PIECES = 6

# Delays (seconds)
LOCK_DELAY = 0.5
FALL_DELAY = 1
AUTOREPEAT_DELAY = 0.300
AUTOREPEAT_PERIOD = 0.010
PARTICULE_ACCELERATION = 1.1
EXPLOSION_ANIMATION = 1

# Piece init coord
MATRIX_PIECE_COORD = Coord(4, LINES)
NEXT_PIECES_COORDS = [Coord(COLLUMNS + 4, LINES - 4 * n) for n in range(NEXT_PIECES)]
HELD_PIECE_COORD = Coord(-5, LINES)

# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_MIN_WIDTH = 517
WINDOW_MIN_HEIGHT = 388
WINDOW_TITLE = "TETRARCADE"
BG_COLOR = (7, 11, 21)

# Delays (seconds)
HIGHLIGHT_TEXT_DISPLAY_DELAY = 0.7

# Transparency (0=invisible, 255=opaque)
NORMAL_ALPHA = 255
PRELOCKED_ALPHA = 100
GHOST_ALPHA = 30
MATRIX_BG_ALPHA = 100
BAR_ALPHA = 75

# Mino size
MINO_SIZE = 20
MINO_SPRITE_SIZE = 21

if getattr(sys, "frozen", False):
    # The application is frozen
    PROGRAM_DIR = os.path.dirname(sys.executable)
else:
    # The application is not frozen
    PROGRAM_DIR = os.path.dirname(__file__)
RESOURCES_DIR = os.path.join(PROGRAM_DIR, "resources")

# Sprites
IMAGES_DIR = os.path.join(RESOURCES_DIR, "images")
WINDOW_BG_PATH = os.path.join(IMAGES_DIR, "bg.jpg")
MATRIX_BG_PATH = os.path.join(IMAGES_DIR, "matrix.png")
MINOES_SPRITES_PATH = os.path.join(IMAGES_DIR, "minoes.png")
Color.LOCKED = 7
MINOES_COLOR_ID = {
    Color.BLUE: 0,
    Color.CYAN: 1,
    Color.GREEN: 2,
    Color.MAGENTA: 3,
    Color.ORANGE: 4,
    Color.RED: 5,
    Color.YELLOW: 6,
    Color.LOCKED: 7,
}
TEXTURES = arcade.load_textures(
    MINOES_SPRITES_PATH,
    ((i * MINO_SPRITE_SIZE, 0, MINO_SPRITE_SIZE, MINO_SPRITE_SIZE) for i in range(8)),
)
TEXTURES = {color: TEXTURES[i] for color, i in MINOES_COLOR_ID.items()}

# Music
MUSIC_DIR = os.path.join(RESOURCES_DIR, "musics")
MUSICS_PATHS = (entry.path for entry in os.scandir(MUSIC_DIR))

# Text
TEXT_COLOR = arcade.color.BUBBLES
FONT_NAME = os.path.join(RESOURCES_DIR, "fonts/joystix monospace.ttf")
STATS_TEXT_MARGIN = 40
STATS_TEXT_SIZE = 14
STATS_TEXT_WIDTH = 150
HIGHLIGHT_TEXT_COLOR = arcade.color.BUBBLES
HIGHLIGHT_TEXT_SIZE = 20

# User profile path
if sys.platform == "win32":
    USER_PROFILE_DIR = os.environ.get(
        "appdata", os.path.expanduser("~\Appdata\Roaming")
    )
else:
    USER_PROFILE_DIR = os.environ.get(
        "XDG_DATA_HOME", os.path.expanduser("~/.local/share")
    )
USER_PROFILE_DIR = os.path.join(USER_PROFILE_DIR, "TetrArcade")
HIGH_SCORE_PATH = os.path.join(USER_PROFILE_DIR, ".high_score")
CONF_PATH = os.path.join(USER_PROFILE_DIR, "config.ini")


class Texture:

    NORMAL = 0
    LOCKED = 1


class State:

    STARTING = 0
    PLAYING = 1
    PAUSED = 2
    OVER = 3


class Scheduler(AbstractScheduler):
    def __init__(self):
        self.tasks = {}

    def postpone(self, task, delay):
        _task = lambda _: task()
        self.tasks[task] = _task
        pyglet.clock.schedule_once(_task, delay)

    def cancel(self, task):
        try:
            _task = self.tasks[task]
        except KeyError:
            pass
        else:
            arcade.unschedule(_task)
            del self.tasks[task]

    def reset(self, task, delay):
        try:
            _task = self.tasks[task]
        except KeyError:
            _task = lambda _: task()
            self.tasks[task] = _task
        else:
            arcade.unschedule(_task)
        pyglet.clock.schedule_once(_task, delay)


class MinoSprite(arcade.Sprite):
    def __init__(self, mino, window, alpha):
        super().__init__()
        self.alpha = alpha
        self.window = window
        self.append_texture(TEXTURES[mino.color])
        self.append_texture(TEXTURES[Color.LOCKED])
        self.set_texture(0)
        self.resize()

    def resize(self):
        self.scale = self.window.scale
        self.size = MINO_SIZE * self.window.scale

    def update(self, x, y):
        self.left = self.window.matrix.bg.left + x * self.size
        self.bottom = self.window.matrix.bg.bottom + y * self.size

    def fall(self, lines_cleared):
        self.bottom -= MINO_SIZE * self.window.scale * lines_cleared


class MinoesSprites(arcade.SpriteList):
    def resize(self):
        for sprite in self:
            sprite.resize()
        self.update()


class TetrominoSprites(MinoesSprites):
    def __init__(self, tetromino, window, alpha=NORMAL_ALPHA):
        super().__init__()
        self.tetromino = tetromino
        self.alpha = alpha
        self.window = window
        for mino in tetromino:
            mino.sprite = MinoSprite(mino, window, alpha)
            self.append(mino.sprite)

    def update(self):
        for mino in self.tetromino:
            coord = mino.coord + self.tetromino.coord
            mino.sprite.update(coord.x, coord.y)

    def set_texture(self, texture):
        for mino in self.tetromino:
            mino.sprite.set_texture(texture)
            mino.sprite.scale = self.window.scale


class MatrixSprites(MinoesSprites):
    def __init__(self, matrix):
        super().__init__()
        self.matrix = matrix

    def update(self):
        for y, line in enumerate(self.matrix):
            for x, mino in enumerate(line):
                if mino:
                    mino.sprite.update(x, y)

    def remove_lines(self, lines_to_remove):
        for y in lines_to_remove:
            for mino in self.matrix[y]:
                if mino:
                    self.remove(mino.sprite)


class TetrArcade(TetrisLogic, arcade.Window):
    """Tetris clone with arcade GUI library"""

    timer = Scheduler()

    def __init__(self):
        locale.setlocale(locale.LC_ALL, "")
        self.highlight_texts = []

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

        super().__init__(LINES, COLLUMNS, NEXT_PIECES)
        arcade.Window.__init__(
            self,
            width=self.init_width,
            height=self.init_height,
            title=WINDOW_TITLE,
            resizable=True,
            antialiasing=False,
            fullscreen=self.init_fullscreen,
        )

        arcade.set_background_color(BG_COLOR)
        self.set_minimum_size(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.bg = arcade.Sprite(WINDOW_BG_PATH)
        self.matrix.bg = arcade.Sprite(MATRIX_BG_PATH)
        self.matrix.bg.alpha = MATRIX_BG_ALPHA
        self.matrix.sprites = MatrixSprites(self.matrix)
        self.on_resize(self.init_width, self.init_height)
        self.exploding_minoes = [None for y in range(LINES)]

        if self.play_music:
            try:
                self.music = pyglet.media.Player()
                playlist = itertools.cycle(
                    pyglet.media.load(path) for path in MUSICS_PATHS
                )
                self.music.queue(playlist)
            except:
                Warning("Can't play music.")
                self.music = None
        else:
            self.music = None

        self.state = State.STARTING

    def new_conf(self):
        self.conf["WINDOW"] = {
            "width": WINDOW_WIDTH,
            "height": WINDOW_HEIGHT,
            "fullscreen": False,
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
            "fullscreen": "F11",
        }
        self.conf["MUSIC"] = {"play": True}
        self.conf["AUTO-REPEAT"] = {"delay": 0.3, "period": 0.01}
        self.load_conf()
        if not os.path.exists(USER_PROFILE_DIR):
            os.makedirs(USER_PROFILE_DIR)
        with open(CONF_PATH, "w") as f:
            self.conf.write(f)

    def load_conf(self):
        self.init_width = int(self.conf["WINDOW"]["width"])
        self.init_height = int(self.conf["WINDOW"]["height"])
        self.init_fullscreen = self.conf["WINDOW"].getboolean("fullscreen")

        for action, key in self.conf["KEYBOARD"].items():
            self.conf["KEYBOARD"][action] = key.upper()
        self.key_map = {
            State.STARTING: {
                getattr(arcade.key, self.conf["KEYBOARD"]["start"]): self.new_game,
                getattr(
                    arcade.key, self.conf["KEYBOARD"]["fullscreen"]
                ): self.toggle_fullscreen,
            },
            State.PLAYING: {
                getattr(arcade.key, self.conf["KEYBOARD"]["move left"]): self.move_left,
                getattr(
                    arcade.key, self.conf["KEYBOARD"]["move right"]
                ): self.move_right,
                getattr(arcade.key, self.conf["KEYBOARD"]["soft drop"]): self.soft_drop,
                getattr(arcade.key, self.conf["KEYBOARD"]["hard drop"]): self.hard_drop,
                getattr(
                    arcade.key, self.conf["KEYBOARD"]["rotate clockwise"]
                ): self.rotate_clockwise,
                getattr(
                    arcade.key, self.conf["KEYBOARD"]["rotate counter"]
                ): self.rotate_counter,
                getattr(arcade.key, self.conf["KEYBOARD"]["hold"]): self.hold,
                getattr(arcade.key, self.conf["KEYBOARD"]["pause"]): self.pause,
                getattr(
                    arcade.key, self.conf["KEYBOARD"]["fullscreen"]
                ): self.toggle_fullscreen,
            },
            State.PAUSED: {
                getattr(arcade.key, self.conf["KEYBOARD"]["pause"]): self.resume,
                getattr(
                    arcade.key, self.conf["KEYBOARD"]["fullscreen"]
                ): self.toggle_fullscreen,
            },
            State.OVER: {
                getattr(arcade.key, self.conf["KEYBOARD"]["start"]): self.new_game,
                getattr(
                    arcade.key, self.conf["KEYBOARD"]["fullscreen"]
                ): self.toggle_fullscreen,
            },
        }

        self.AUTOREPEAT_DELAY = float(self.conf["AUTO-REPEAT"]["delay"])
        self.AUTOREPEAT_PERIOD = float(self.conf["AUTO-REPEAT"]["period"])

        controls_text = (
            "\n\n\nCONTROLS\n\n"
            + "\n".join(
                "{:<16s}{:>6s}".format(key, action)
                for key, action in tuple(self.conf["KEYBOARD"].items())
                + (("QUIT", "ALT+F4"),)
            )
            + "\n\n\n"
        )
        self.start_text = (
            "TETRARCADE"
            + controls_text
            + "PRESS [{}] TO START".format(self.conf["KEYBOARD"]["start"])
        )
        self.pause_text = (
            "PAUSE"
            + controls_text
            + "PRESS [{}] TO RESUME".format(self.conf["KEYBOARD"]["pause"])
        )
        self.game_over_text = """GAME
OVER

PRESS
[{}]
TO PLAY
AGAIN""".format(
            self.conf["KEYBOARD"]["start"]
        )

        self.play_music = self.conf["MUSIC"].getboolean("play")

    def on_new_game(self, matrix, next_pieces):
        self.highlight_texts = []

        self.matrix.sprites = MatrixSprites(matrix)
        for piece in next_pieces:
            piece.sprites = TetrominoSprites(piece, self)

        if self.music:
            self.music.seek(0)
            self.music.play()

        self.state = State.PLAYING

    def on_new_level(self, level):
        self.show_text("LEVEL\n{:n}".format(level))

    def on_generation_phase(self, matrix, falling_piece, ghost_piece, next_pieces):
        matrix.sprites.update()
        falling_piece.sprites = TetrominoSprites(falling_piece, self)
        ghost_piece.sprites = TetrominoSprites(ghost_piece, self, GHOST_ALPHA)
        next_pieces[-1].sprites = TetrominoSprites(next_pieces[-1], self)
        for piece, coord in zip(next_pieces, NEXT_PIECES_COORDS):
            piece.coord = coord
        for piece in [falling_piece, ghost_piece] + next_pieces:
            piece.sprites.update()

    def on_falling_phase(self, falling_piece, ghost_piece):
        falling_piece.sprites.set_texture(Texture.NORMAL)
        falling_piece.sprites.update()
        ghost_piece.sprites.update()

    def on_locked(self, falling_piece, ghost_piece):
        falling_piece.sprites.set_texture(Texture.LOCKED)
        falling_piece.sprites.update()
        ghost_piece.sprites.update()

    def on_locks_down(self, matrix, falling_piece):
        falling_piece.sprites.set_texture(Texture.NORMAL)
        for mino in falling_piece:
            matrix.sprites.append(mino.sprite)

    def on_animate_phase(self, matrix, lines_to_remove):
        if not lines_to_remove:
            return

        self.timer.cancel(self.clean_particules)
        for y in lines_to_remove:
            line_textures = tuple(TEXTURES[mino.color] for mino in matrix[y])
            self.exploding_minoes[y] = arcade.Emitter(
                center_xy=(matrix.bg.left, matrix.bg.bottom + (y + 0.5) * MINO_SIZE),
                emit_controller=arcade.EmitBurst(COLLUMNS),
                particle_factory=lambda emitter: arcade.LifetimeParticle(
                    filename_or_texture=random.choice(line_textures),
                    change_xy=arcade.rand_in_rect(
                        (-COLLUMNS * MINO_SIZE, -4 * MINO_SIZE),
                        2 * COLLUMNS * MINO_SIZE,
                        5 * MINO_SIZE,
                    ),
                    lifetime=EXPLOSION_ANIMATION,
                    center_xy=arcade.rand_on_line((0, 0), (matrix.bg.width, 0)),
                    scale=self.scale,
                    alpha=NORMAL_ALPHA,
                    change_angle=2,
                ),
            )
        self.timer.postpone(self.clean_particules, EXPLOSION_ANIMATION)

    def clean_particules(self):
        self.exploding_minoes = [None for y in range(LINES)]

    def on_eliminate_phase(self, matrix, lines_to_remove):
        matrix.sprites.remove_lines(lines_to_remove)

    def on_completion_phase(self, pattern_name, pattern_score, nb_combo, combo_score):
        if pattern_score:
            self.show_text("{:s}\n{:n}".format(pattern_name, pattern_score))
        if combo_score:
            self.show_text("COMBO x{:n}\n{:n}".format(nb_combo, combo_score))

    def on_hold(self, held_piece):
        held_piece.coord = HELD_PIECE_COORD
        if type(held_piece) == I_Tetrimino:
            held_piece.coord += Movement.LEFT
        held_piece.sprites.set_texture(Texture.NORMAL)
        held_piece.sprites.update()

    def on_pause(self):
        self.state = State.PAUSED
        if self.music:
            self.music.pause()

    def resume(self):
        if self.music:
            self.music.play()
        self.state = State.PLAYING

    def on_game_over(self):
        self.state = State.OVER
        if self.music:
            self.music.pause()

    def on_key_press(self, key, modifiers):
        try:
            action = self.key_map[self.state][key]
        except KeyError:
            return
        else:
            self.do_action(action)

    def on_key_release(self, key, modifiers):
        try:
            action = self.key_map[self.state][key]
        except KeyError:
            return
        else:
            self.remove_action(action)

    def show_text(self, text):
        self.highlight_texts.append(text)
        self.timer.postpone(self.del_highlight_text, HIGHLIGHT_TEXT_DISPLAY_DELAY)

    def del_highlight_text(self):
        if self.highlight_texts:
            self.highlight_texts.pop(0)
        else:
            self.timer.cancel(self.del_highlight_text)

    def on_draw(self):
        arcade.start_render()
        self.bg.draw()

        if self.state not in (State.STARTING, State.PAUSED):
            self.matrix.bg.draw()
            self.matrix.sprites.draw()

            for tetromino in [
                self.held.piece,
                self.matrix.piece,
                self.matrix.ghost,
            ] + self.next.pieces:
                if tetromino:
                    tetromino.sprites.draw()

            t = time.localtime(self.stats.time)
            font_size = STATS_TEXT_SIZE * self.scale
            for y, text in enumerate(
                ("TIME", "LINES", "GOAL", "LEVEL", "HIGH SCORE", "SCORE")
            ):
                arcade.draw_text(
                    text=text,
                    start_x=self.matrix.bg.left
                    - self.scale * (STATS_TEXT_MARGIN + STATS_TEXT_WIDTH),
                    start_y=self.matrix.bg.bottom + 1.5 * (2 * y + 1) * font_size,
                    color=TEXT_COLOR,
                    font_size=font_size,
                    align="right",
                    font_name=FONT_NAME,
                    anchor_x="left",
                )
            for y, text in enumerate(
                (
                    "{:02d}:{:02d}:{:02d}".format(t.tm_hour - 1, t.tm_min, t.tm_sec),
                    "{:n}".format(self.stats.lines_cleared),
                    "{:n}".format(self.stats.goal),
                    "{:n}".format(self.stats.level),
                    "{:n}".format(self.stats.high_score),
                    "{:n}".format(self.stats.score),
                )
            ):
                arcade.draw_text(
                    text=text,
                    start_x=self.matrix.bg.left - STATS_TEXT_MARGIN * self.scale,
                    start_y=self.matrix.bg.bottom + 3 * y * font_size,
                    color=TEXT_COLOR,
                    font_size=font_size,
                    align="right",
                    font_name=FONT_NAME,
                    anchor_x="right",
                )

        for exploding_minoes in self.exploding_minoes:
            if exploding_minoes:
                exploding_minoes.draw()

        highlight_text = {
            State.STARTING: self.start_text,
            State.PLAYING: self.highlight_texts[0] if self.highlight_texts else "",
            State.PAUSED: self.pause_text,
            State.OVER: self.game_over_text,
        }.get(self.state, "")
        if highlight_text:
            arcade.draw_text(
                text=highlight_text,
                start_x=self.matrix.bg.center_x,
                start_y=self.matrix.bg.center_y,
                color=HIGHLIGHT_TEXT_COLOR,
                font_size=HIGHLIGHT_TEXT_SIZE * self.scale,
                align="center",
                font_name=FONT_NAME,
                anchor_x="center",
                anchor_y="center",
            )

    def on_hide(self):
        self.pause()

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        center_x = width / 2
        center_y = height / 2
        self.scale = min(width / WINDOW_WIDTH, height / WINDOW_HEIGHT)

        self.bg.scale = max(width / WINDOW_WIDTH, height / WINDOW_HEIGHT)
        self.bg.center_x = center_x
        self.bg.center_y = center_y

        self.matrix.bg.scale = self.scale
        self.matrix.bg.center_x = center_x
        self.matrix.bg.center_y = center_y
        self.matrix.bg.left = int(self.matrix.bg.left)
        self.matrix.bg.top = int(self.matrix.bg.top)

        self.matrix.sprites.resize()

        for tetromino in [
            self.held.piece,
            self.matrix.piece,
            self.matrix.ghost,
        ] + self.next.pieces:
            if tetromino:
                tetromino.sprites.resize()

    def load_high_score(self):
        try:
            with open(HIGH_SCORE_PATH, "rb") as f:
                crypted_high_score = f.read()
                super().load_high_score(crypted_high_score)
        except:
            self.stats.high_score = 0

    def save_high_score(self):
        try:
            if not os.path.exists(USER_PROFILE_DIR):
                os.makedirs(USER_PROFILE_DIR)
            with open(HIGH_SCORE_PATH, mode="wb") as f:
                crypted_high_score = super().save_high_score()
                f.write(crypted_high_score)
        except Exception as e:
            sys.exit(
                """High score: {:n}
High score could not be saved:
""".format(
                    self.high_score
                )
                + str(e)
            )

    def update(self, delta_time):
        for exploding_minoes in self.exploding_minoes:
            if exploding_minoes:
                exploding_minoes.update()

    def on_close(self):
        self.save_high_score()
        if self.music:
            self.music.pause()
        super().on_close()


def main():
    try:
        TetrArcade()
        arcade.run()
    except Exception as e:
        sys.exit(e)


if __name__ == "__main__":
    main()
