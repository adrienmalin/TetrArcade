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

from tetrislogic import TetrisLogic, State


# Constants
# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "TETRARCADE"
BG_COLOR = (7, 11, 21)

# Delays (seconds)
HIGHLIGHT_TEXT_DISPLAY_DELAY = 0.7

# Transparency (0=invisible, 255=opaque)
NORMAL_ALPHA = 200
PRELOCKED_ALPHA = 100
GHOST_ALPHA = 30
MATRIX_SPRITE_ALPHA = 100

# Paths
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
            
            
class ResizableSprite(arcade.Sprite):
    
    def __init__(self, path):
        super().__init__(path)
        self.init_width = self.width
        self.init_height = self.height
        
    def resize(self, ratio):
        self.width = ratio * self.init_width
        self.height = ratio * self.init_height


class MinoSprites(arcade.SpriteList):

    def __init__(self, matrix):
        super().__init__()
        self.matrix = matrix

    def update_mino(self, mino, x, y, alpha):
        mino.sprite.left = self.matrix.sprite.left + x*(mino.sprite.width-1)
        mino.sprite.bottom = self.matrix.sprite.bottom + y*(mino.sprite.height-1)
        mino.sprite.alpha = alpha
        
    def resize(self, ratio):
        for sprite in self:
            sprite.resize(ratio)
            self.update(sprite)


class MatrixSprites(MinoSprites):
        
    def update(self):
        for sprite in self.matrix.sprites:
            self.matrix.sprite.remove(sprite)
        for y, line in enumerate(self.matrix):
            for x, mino in enumerate(line):
                if mino:
                    self.update_mino(mino, x, y, NORMAL_ALPHA)
                    self.append(mino.sprite)


class TetrominoSprites(MinoSprites):

    def __init__(self, tetromino, matrix, alpha=NORMAL_ALPHA):
        super().__init__(matrix)
        self.tetromino = tetromino
        path = MINOES_SPRITES_PATHS[tetromino.MINOES_COLOR]
        self.alpha = alpha
        for mino in tetromino:
            mino.sprite = ResizableSprite(path)
            self.append(mino.sprite)

    def update(self):
        alpha = (
            PRELOCKED_ALPHA
            if self.tetromino.prelocked
            else self.alpha
        )
        for mino in self.tetromino:
            coord = mino.coord + self.tetromino.coord
            self.update_mino(mino, coord.x, coord.y, alpha)


class TetrArcade(TetrisLogic, arcade.Window):

    def __init__(self):
        locale.setlocale(locale.LC_ALL, '')
        self.highlight_texts = []
        self.tasks = {}

        self.KEY_MAP = {
            State.STARTING: {
                arcade.key.ENTER:     self.new_game,
                arcade.key.F11:       self.toogle_fullscreen
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
            State.PAUSED: {
                arcade.key.ESCAPE:    self.resume,
                arcade.key.F1:        self.resume,
                arcade.key.F11:       self.toogle_fullscreen
            },
            State.OVER: {
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

        self.init_width = self.width
        self.init_height = self.height
        self.sprite = ResizableSprite(WINDOW_BG_PATH)
        self.matrix.sprite = ResizableSprite(MATRIX_SPRITE_PATH)
        self.matrix.sprite.alpha = MATRIX_SPRITE_ALPHA
        self.matrix.sprites = MatrixSprites(self.matrix)
        self.stats_text = arcade.create_text(
            text = STATS_TEXT,
            color = TEXT_COLOR,
            font_size = FONT_SIZE,
            font_name = FONT_NAME,
            anchor_x = 'right'
        )
        self.highlight_text_size = HIGHLIGHT_TEXT_SIZE
        arcade.set_background_color(BG_COLOR)
        
    def on_resize(self, width, height):
        super().on_resize(width, height)
        center_x = width / 2
        center_y = height / 2
        self.sprite.center_x = center_x
        self.sprite.center_y = center_y
        self.matrix.sprite.center_x = center_x
        self.matrix.sprite.center_y = center_y
        self.matrix.sprite.left = int(self.matrix.sprite.left)
        self.matrix.sprite.top = int(self.matrix.sprite.top)
        ratio = min(
            width / self.init_width,
            height / self.init_height
        )
        for sprite in [
            self.sprite,
            self.matrix.sprite
        ]:
            sprite.resize(ratio)
        for minoes in [self.matrix, self.held, self.current, self.ghost] + self.next:
            minoes.sprites.resize(ratio)
        self.font_size = FONT_SIZE * ratio
        self.stats_text = arcade.create_text(
            text = STATS_TEXT,
            color = TEXT_COLOR,
            font_size = FONT_SIZE,
            font_name = FONT_NAME,
            anchor_x = 'right'
        )
        self.highlight_text_size = HIGHLIGHT_TEXT_SIZE * ratio
        
    def toogle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        
    def new_game(self):
        self.highlight_texts = []
        self.matrix.sprites = MatrixSprites(self.matrix)
        super().new_game()

    def new_next(self):
        super().new_next()
        self.next[-1].sprites = TetrominoSprites(self.next[-1], self.matrix)

    def new_current(self):
        super().new_current()
        self.ghost.sprites = TetrominoSprites(self.ghost, self.matrix, GHOST_ALPHA)
        for tetromino in [self.current, self.ghost] + self.next:
            tetromino.sprites.update()

    def move(self, movement, prelock=True):
        moved = super().move(movement, prelock)
        if moved or self.current.prelocked:
            for tetromino in (self.current, self.ghost):
                tetromino.sprites.update()
        return moved

    def rotate(self, rotation):
        rotated = super().rotate(rotation)
        if rotated:
            for tetromino in (self.current, self.ghost):
                tetromino.sprites.update()
        return rotated

    def swap(self):
        super().swap()
        self.ghost.sprites = TetrominoSprites(self.ghost, self.matrix, GHOST_ALPHA)
        for tetromino in [self.held, self.current, self.ghost]:
            if tetromino:
                tetromino.sprites.update()

    def lock(self):
        self.current.sprites.update()
        super().lock()
        self.matrix.sprites.update()

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
        self.sprite.draw()

        if self.state in (State.PLAYING, State.OVER):
            self.matrix.sprite.draw()
            self.matrix.sprites.draw()
            for tetromino in [self.held, self.current, self.ghost] + self.next:
                if tetromino:
                    tetromino.sprites.draw()

            arcade.render_text(
                self.stats_text,
                self.matrix.sprite.left - TEXT_MARGIN,
                self.matrix.sprite.bottom
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
                    start_x = self.matrix.sprite.left - TEXT_MARGIN,
                    start_y = self.matrix.sprite.bottom + 2*y*TEXT_HEIGHT,
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
                start_x = self.matrix.sprite.center_x,
                start_y = self.matrix.sprite.center_y,
                color = HIGHLIGHT_TEXT_COLOR,
                font_size = self.highlight_text_size,
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
