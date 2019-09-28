# -*- coding: utf-8 -*-
import sys
import locale
import time

try:
    import arcade
except ImportError:
    sys.exit(
"""This game require arcade library.
You can install it with:
python -m pip install --user arcade
"""
)

from tetris import Tetris, Status, Scheduler


# Constants
# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "TETRARCADE"

# Delays (seconds)
AUTOREPEAT_DELAY = 0.220    # Official : 0.300
AUTOREPEAT_INTERVAL = 0.010 # Official : 0.010
HIGHLIGHT_TEXT_DISPLAY_DELAY = 1

# Text
TEXT_COLOR = arcade.color.BUBBLES
HIGHLIGHT_TEXT_COLOR = arcade.color.BUBBLES
FONT_NAME = "joystix monospace.ttf"
TEXT_MARGIN = 40
FONT_SIZE = 10
HIGHLIGHT_TEXT_FONT_SIZE = 20
TEXT_HEIGHT = 13.2
START_TEXT = """PRESS
[ENTER]
TO
START"""
STATS_TEXT = """SCORE
HIGH SCORE
TIME
LEVEL
GOAL
LINES




MOVE LEFT        ←
MOVE RIGHT       →
SOFT DROP        ↓
HARD DROP    SPACE
ROTATE           ↑
CLOCKWISE
ROTATE           Z
COUNTERCLOCKWISE
HOLD             C
PAUSE          ESC"""
GAME_OVER_TEXT = """GAME
OVER

PRESS
[ENTER]
TO PLAY
AGAIN"""
PAUSE_TEXT = """PAUSE

PRESS
[ESC]
TO
RESUME"""

# Sprites paths
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

# Transparency (0=invisible, 255=opaque)
NORMAL_ALPHA = 200
PRELOCKED_ALPHA = 127
GHOST_ALPHA = 50
MATRIX_SRITE_ALPHA = 100


class ArcadeScheduler(Scheduler):

    def __init__(self):
        self._tasks = {}

    def start(self, task, period):
        def _task(delta_time):
            task()
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


class TetrArcade(Tetris, arcade.Window):

    scheduler = ArcadeScheduler()

    def __init__(self):
        super().__init__()

        locale.setlocale(locale.LC_ALL, '')

        self.actions = {
            Status.STARTING: {
                arcade.key.ENTER:     self.new_game
            },
            Status.PLAYING: {
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
            Status.PAUSED: {
                arcade.key.ESCAPE:    self.resume,
                arcade.key.F1:        self.resume
            },
            Status.OVER: {
                arcade.key.ENTER:     self.new_game
            }
        }
        self.autorepeatable_actions = (self.move_left, self.move_right, self.soft_drop)

        self.highlight_texts = []
        self.pressed_actions = []

        arcade.Window.__init__(
            self,
            width = WINDOW_WIDTH,
            height = WINDOW_HEIGHT,
            title = WINDOW_TITLE,
            resizable = False,
            antialiasing = False
        )

        self.bg_sprite = arcade.Sprite(WINDOW_BG)
        self.matrix_minoes_sprites = arcade.SpriteList()
        self.held_piece_sprites = arcade.SpriteList()
        self.current_piece_sprites = arcade.SpriteList()
        self.ghost_piece_sprites = arcade.SpriteList()
        self.next_pieces_sprites = arcade.SpriteList()
        self.matrix_sprite = arcade.Sprite(MATRIX_SPRITE_PATH)
        self.matrix_sprite.alpha = MATRIX_SRITE_ALPHA
        self.on_resize(self.width, self.height)
        self.general_text = arcade.create_text(
            text = STATS_TEXT,
            color = TEXT_COLOR,
            font_size = FONT_SIZE,
            font_name = FONT_NAME,
            anchor_x = 'right'
        )

    def new_game(self):
        self.highlight_texts = []
        self.pressed_actions = []
        self.auto_repeat = False
        super().new_game()

    def new_current_piece(self):
        super().new_current_piece()
        self.reload_next_pieces()
        self.reload_current_piece()
        self.reload_matrix()

    def lock(self):
        super().lock()
        if self.pressed_actions:
            self.stop_autorepeat()
            self.scheduler.start(self.repeat_action, AUTOREPEAT_DELAY)

    def swap(self):
        super().swap()
        self.reload_held_piece()
        self.reload_current_piece()

    def pause(self):
        super().pause()
        self.pressed_actions = []
        self.stop_autorepeat()

    def game_over(self):
        super().game_over()
        self.scheduler.stop(self.repeat_action)

    def on_key_press(self, key, modifiers):
        for key_or_modifier in (key, modifiers):
            try:
                action = self.actions[self.status][key_or_modifier]
            except KeyError:
                pass
            else:
                action()
                if action in self.autorepeatable_actions:
                    self.stop_autorepeat()
                    self.pressed_actions.append(action)
                    self.scheduler.start(self.repeat_action, AUTOREPEAT_DELAY)

    def on_key_release(self, key, modifiers):
        try:
            action = self.actions[self.status][key]
        except KeyError:
            pass
        else:
            if action in self.autorepeatable_actions:
                try:
                    self.pressed_actions.remove(action)
                except ValueError:
                    pass

    def repeat_action(self):
        if self.pressed_actions:
            self.pressed_actions[-1]()
            if not self.auto_repeat:
                self.auto_repeat = True
                self.scheduler.stop(self.repeat_action)
                self.scheduler.start(self.repeat_action, AUTOREPEAT_INTERVAL)
        else:
            self.stop_autorepeat()

    def stop_autorepeat(self):
        self.auto_repeat = False
        self.scheduler.stop(self.repeat_action)

    def show_text(self, text):
        self.highlight_texts.append(text)
        self.scheduler.start(self.del_highlight_text, HIGHLIGHT_TEXT_DISPLAY_DELAY)

    def del_highlight_text(self):
        if self.highlight_texts:
            self.highlight_texts.pop(0)
        else:
            self.scheduler.stop(self.del_highlight_text)

    def reload_piece(self, piece):
        piece_sprites = arcade.SpriteList()
        for mino_position in piece.minoes_positions:
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
            for mino_position in piece.minoes_positions:
                mino_sprite_path = MINOES_SPRITES_PATHS[piece.MINOES_COLOR]
                mino_sprite = arcade.Sprite(mino_sprite_path)
                mino_sprite.alpha = NORMAL_ALPHA
                self.next_pieces_sprites.append(mino_sprite)

    def reload_current_piece(self):
        self.current_piece_sprites = self.reload_piece(self.current_piece)
        self.ghost_piece_sprites = self.reload_piece(self.ghost_piece)

    def reload_matrix(self):
        if self.matrix:
            self.matrix_minoes_sprites = arcade.SpriteList()
            for y, line in enumerate(self.matrix):
                for x, mino_color in enumerate(line):
                    if mino_color:
                        mino_sprite_path = MINOES_SPRITES_PATHS[mino_color]
                        mino_sprite = arcade.Sprite(mino_sprite_path)
                        mino_sprite.left = self.matrix_sprite.left + x*(mino_sprite.width-1)
                        mino_sprite.bottom = self.matrix_sprite.bottom + y*(mino_sprite.height-1)
                        mino_sprite.alpha = 200
                        self.matrix_minoes_sprites.append(mino_sprite)

    def update_piece(self, piece, piece_sprites):
        if piece:
            for mino_sprite, mino_position in zip(
                piece_sprites, piece.minoes_positions
            ):
                mino_position += piece.position
                mino_sprite.left = self.matrix_sprite.left + mino_position.x*(mino_sprite.width-1)
                mino_sprite.bottom = self.matrix_sprite.bottom + mino_position.y*(mino_sprite.height-1)

    def on_draw(self):
        arcade.start_render()
        self.bg_sprite.draw()

        if self.status in (Status.PLAYING, Status.OVER):
            self.matrix_sprite.draw()
            self.matrix_minoes_sprites.draw()

            self.update_piece(self.held_piece, self.held_piece_sprites)
            self.held_piece_sprites.draw()

            self.update_piece(self.current_piece, self.current_piece_sprites)
            if self.current_piece.prelocked:
                alpha = PRELOCKED_ALPHA if self.current_piece.prelocked else NORMAL_ALPHA
                for mino_sprite in self.current_piece_sprites:
                    mino_sprite.alpha = alpha
            self.current_piece_sprites.draw()

            self.update_piece(self.ghost_piece, self.ghost_piece_sprites)
            for mino_sprite in self.ghost_piece_sprites:
                mino_sprite.alpha = GHOST_ALPHA
            self.ghost_piece_sprites.draw()

            for n, piece in enumerate(self.next_pieces):
                for mino_sprite, mino_position in zip(
                    self.next_pieces_sprites[4*n:4*(n+1)], piece.minoes_positions
                ):
                    mino_position += piece.position
                    mino_sprite.left = self.matrix_sprite.left + mino_position.x*(mino_sprite.width-1)
                    mino_sprite.bottom = self.matrix_sprite.bottom + mino_position.y*(mino_sprite.height-1)
            self.next_pieces_sprites.draw()

            arcade.render_text(
                self.general_text,
                self.matrix_sprite.left - TEXT_MARGIN,
                self.matrix_sprite.bottom
            )
            t = time.localtime(self.time)
            for y, text in enumerate(
                (
                    "{:n}".format(self.nb_lines),
                    "{:n}".format(self.goal),
                    "{:n}".format(self.level),
                    "{:02d}:{:02d}:{:02d}".format(t.tm_hour-1, t.tm_min, t.tm_sec),
                    "{:n}".format(self.high_score),
                    "{:n}".format(self.score)
                ),
                start=14
            ):
                arcade.draw_text(
                    text = text,
                    start_x = self.matrix_sprite.left - TEXT_MARGIN,
                    start_y = self.matrix_sprite.bottom + y*TEXT_HEIGHT,
                    color = TEXT_COLOR,
                    font_size = FONT_SIZE,
                    align = 'right',
                    font_name = FONT_NAME,
                    anchor_x = 'right'
                )

        highlight_text = {
            Status.STARTING: START_TEXT,
            Status.PLAYING: self.highlight_texts[0] if self.highlight_texts else "",
            Status.PAUSED: PAUSE_TEXT,
            Status.OVER: GAME_OVER_TEXT
        }.get(self.status, "")
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

    def on_resize(self, width, height):
        center_x = self.width / 2
        center_y = self.height / 2
        self.bg_sprite.center_x = center_x
        self.bg_sprite.center_y = center_y
        self.matrix_sprite.center_x = center_x
        self.matrix_sprite.center_y = center_y
        self.matrix_sprite.left = int(self.matrix_sprite.left)
        self.matrix_sprite.top = int(self.matrix_sprite.top)
        self.reload_matrix()


def main():
    TetrArcade()
    arcade.run()

if __name__ == "__main__":
    main()
