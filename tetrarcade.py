# -*- coding: utf-8 -*-
import sys
try:
    import arcade
except ImportError:
    sys.exit(
"""This game require arcade library.
You can install it with:
python -m pip install --user arcade
"""
)
import random


# Constants
# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "TETRARCADE"

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
NORMAL_ALPHA = 200
PRELOCKED_ALPHA = 127
GHOST_ALPHA = 50

# Sound paths
MUSIC_PATH = "sounds/music.mp3"

# Matrix
NB_LINES = 20
NB_COLS = 10

# Delays
AUTOREPEAT_DELAY = 0.170    # Official : 0.300
AUTOREPEAT_INTERVAL = 0.010 # Official : 0.010
LOCK_DELAY = 0.5
FALL_DELAY = 1


class Coord:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coord(self.x+other.x, self.y+other.y)


# Piece init position
MATRIX_PIECE_INIT_POSITION = Coord(4, NB_LINES)
NEXT_PIECE_POSITION = Coord(NB_COLS+3, NB_LINES-4)
HELD_PIECE_POSITION = Coord(-4, NB_LINES-4)
HELD_I_POSITION = Coord(-5, NB_LINES-4)


class Status:
    
    STARTING = "starting"
    PLAYING =  "playing"
    PAUSED =   "paused"
    OVER =     "over"


class Movement:
    
    LEFT  = Coord(-1, 0)
    RIGHT = Coord(1, 0)
    DOWN  = Coord(0, -1)


class Rotation:
    
    CLOCKWISE = -1
    COUNTERCLOCKWISE = 1
    
    
class T_Spin:
    
    NO_T_SPIN =   ""
    MINI_T_SPIN = "MINI T-SPIN"
    T_SPIN =      "T-SPIN"
  
    
class Tetromino:
    
    
    class TetrominoBase:
        # Super rotation system
        SRS = {
            Rotation.COUNTERCLOCKWISE: (
                (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
                (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, 2), Coord(-1, 2)),
                (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
                (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2))
            ),
            Rotation.CLOCKWISE: (
                (Coord(0, 0), Coord(-1, 0), Coord(-1, 1), Coord(0, -2), Coord(-1, -2)),
                (Coord(0, 0), Coord(-1, 0), Coord(-1, -1), Coord(0, -2), Coord(-1, 2)),
                (Coord(0, 0), Coord(1, 0), Coord(1, 1), Coord(0, -2), Coord(1, -2)),
                (Coord(0, 0), Coord(1, 0), Coord(1, -1), Coord(0, 2), Coord(1, 2))
            )
        }
        lock_delay = LOCK_DELAY
        fall_delay = FALL_DELAY
        
        def __init__(self):
            self.position = NEXT_PIECE_POSITION
            self.minoes_positions = self.MINOES_POSITIONS
            self.orientation = 0
            self.last_rotation_point_used = None
            self.hold_enabled = True
            self.prelocked = False
            
        def ghost(self):
            return self.__class__()
    
    
    class O(TetrominoBase):
        
        SRS = {
            Rotation.COUNTERCLOCKWISE: (tuple(), tuple(), tuple(), tuple()),
            Rotation.CLOCKWISE: (tuple(), tuple(), tuple(), tuple())
        }
        MINOES_POSITIONS = (Coord(0, 0), Coord(1, 0), Coord(0, 1), Coord(1, 1))
        MINOES_COLOR = "yellow"
    
        def rotate(self, direction):
            return False
    
    
    class I(TetrominoBase):
        
        SRS = {
            Rotation.COUNTERCLOCKWISE: (
                (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2)),
                (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2)),
                (Coord(0, 1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2)),
                (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2))
            ),
            Rotation.CLOCKWISE: (
                (Coord(1, 0), Coord(-1, 0), Coord(2, 0), Coord(-1, -1), Coord(2, 2)),
                (Coord(0, -1), Coord(1, 1), Coord(-2, 1), Coord(1, -1), Coord(-2, 2)),
                (Coord(-1, 0), Coord(1, 0), Coord(-2, 0), Coord(1, 1), Coord(-2, -2)),
                (Coord(0, -1), Coord(-1, -1), Coord(2, -1), Coord(-1, 1), Coord(2, -2))
            )
        }
        MINOES_POSITIONS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(2, 0))
        MINOES_COLOR = "cyan"
    
    
    class T(TetrominoBase):
        
        MINOES_POSITIONS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 0))
        MINOES_COLOR = "magenta"
    
    
    class L(TetrominoBase):
        
        MINOES_POSITIONS = (Coord(-1, 0), Coord(0, 0), Coord(1, 0), Coord(1, 1))
        MINOES_COLOR = "orange"
    
    
    class J(TetrominoBase):
        
        MINOES_POSITIONS = (Coord(-1, 1), Coord(-1, 0), Coord(0, 0), Coord(1, 0))
        MINOES_COLOR = "blue"
    
    
    class S(TetrominoBase):
        
        MINOES_POSITIONS = (Coord(-1, 0), Coord(0, 0), Coord(0, 1), Coord(1, 1))
        MINOES_COLOR = "green"
    
    
    class Z(TetrominoBase):
        
        MINOES_POSITIONS = (Coord(-1, 1), Coord(0, 1), Coord(0, 0), Coord(1, 0))
        MINOES_COLOR = "red"
        
        
    TETROMINOES = (O, I, T, L, J, S, Z)
    random_bag = []
    
    def __new__(cls):
        if not cls.random_bag:
            cls.random_bag = list(cls.TETROMINOES)
            random.shuffle(cls.random_bag)
        return cls.random_bag.pop()()
        
    
class GameLogic():
    
    T_SLOT = (Coord(-1, 1), Coord(1, 1), Coord(1, -1), Coord(-1, -1))
    SCORES = (
        {"name": "", T_Spin.NO_T_SPIN: 0, T_Spin.MINI_T_SPIN: 1, T_Spin.T_SPIN: 4},
        {"name": "SINGLE", T_Spin.NO_T_SPIN: 1, T_Spin.MINI_T_SPIN: 2, T_Spin.T_SPIN: 8},
        {"name": "DOUBLE", T_Spin.NO_T_SPIN: 3, T_Spin.MINI_T_SPIN: 12},
        {"name": "TRIPLE", T_Spin.NO_T_SPIN: 5, T_Spin.T_SPIN: 16},
        {"name": "TETRIS", T_Spin.NO_T_SPIN: 8}
    )
    
    def __init__(self, ui):
        self.ui = ui
        self.high_score = 0
        self.status = Status.STARTING
        
    def new_game(self):
        self.level = 0
        self.score = 0
        self.nb_lines = 0
        self.goal = 0
        
        self.lock_delay = LOCK_DELAY
        self.fall_delay = FALL_DELAY
        
        self.matrix = [
            [None for x in range(NB_COLS)]
            for y in range(NB_LINES+3)
        ]
        self.next_piece = Tetromino()
        self.current_piece = None
        self.held_piece = None
        self.status = Status.PLAYING
        self.new_level()
        self.new_current_piece()
    
    def new_level(self):
        self.level += 1
        self.goal += 5 * self.level
        if self.level <= 20:
            self.fall_delay = pow(0.8 - ((self.level-1)*0.007), self.level-1)
        if self.level > 15:
            self.lock_delay = 0.5 * pow(0.9, self.level-15)
        self.ui.display_new_level(self.level)
        
    def new_current_piece(self):
        self.current_piece = self.next_piece
        self.current_piece.position = MATRIX_PIECE_INIT_POSITION
        self.ghost_piece = self.current_piece.ghost()
        self.move_ghost()
        self.ui.new_current_piece()
        self.next_piece = Tetromino()
        self.ui.new_next_piece()
        if self.can_move(
            self.current_piece.position,
            self.current_piece.minoes_positions
        ):
            self.ui.start_fall()
        else:
            self.game_over()

    def cell_is_free(self, position):
        return (
            0 <= position.x < NB_COLS
            and 0 <= position.y
            and not self.matrix[position.y][position.x]
        )
        
    def can_move(self, potential_position, minoes_positions):
        return all(
            self.cell_is_free(potential_position+mino_position)
            for mino_position in minoes_positions
        )
        
    def move(self, movement, prelock_on_stuck=True):
        potential_position = self.current_piece.position + movement
        if self.can_move(potential_position, self.current_piece.minoes_positions):
            if self.current_piece.prelocked:
                self.ui.prelock(restart=True)
            self.current_piece.position = potential_position
            self.current_piece.last_rotation_point_used = None
            self.move_ghost()
            return True
        else:
            if (
                prelock_on_stuck and not self.current_piece.prelocked
                and movement == Movement.DOWN
            ):
                self.current_piece.prelocked = True
                self.ui.prelock()
            return False

    def rotate(self, direction):
        rotated_minoes_positions = tuple(
            Coord(-direction*mino_position.y, direction*mino_position.x)
            for mino_position in self.current_piece.minoes_positions
        )
        for rotation_point, liberty_degree in enumerate(
            self.current_piece.SRS[direction][self.current_piece.orientation],
            start = 1
        ):
            potential_position = self.current_piece.position + liberty_degree
            if self.can_move(potential_position, rotated_minoes_positions):
                if self.current_piece.prelocked:
                    self.ui.prelock(restart=True)
                self.current_piece.position = potential_position
                self.current_piece.minoes_positions = rotated_minoes_positions
                self.current_piece.orientation = (
                    (self.current_piece.orientation + direction) % 4
                )
                self.current_piece.last_rotation_point_used = rotation_point
                self.move_ghost()
                return True
        else:
            return False
        
    def move_ghost(self):
        self.ghost_piece.position = self.current_piece.position
        self.ghost_piece.minoes_positions = self.current_piece.minoes_positions
        while self.can_move(
            self.ghost_piece.position + Movement.DOWN,
            self.ghost_piece.minoes_positions
        ):
            self.ghost_piece.position += Movement.DOWN
        
    def soft_drop(self):
        if self.move(Movement.DOWN):
            self.score += 1
            return True
        else:
            return False

    def hard_drop(self):
        drop_score = 0
        while self.move(Movement.DOWN, prelock_on_stuck=False):
            drop_score += 2
        self.score += drop_score
        return drop_score
        
    def lock(self):
        if self.move(Movement.DOWN):
            self.ui.stop_fall()
            self.ui.cancel_prelock()
            return
            
        if all(
            (mino_position + self.current_piece.position).y >= NB_LINES
            for mino_position in self.current_piece.minoes_positions
        ):
            self.current_piece.prelocked = False
            self.ui.update_current_piece()
            self.game_over()
            return
        
        for mino_position in self.current_piece.minoes_positions:
            position = mino_position + self.current_piece.position
            if position.y <= NB_LINES+3:
                self.matrix[position.y][position.x] = self.current_piece.MINOES_COLOR

        nb_lines_cleared = 0
        for y, line in reversed(list(enumerate(self.matrix))):
            if all(mino for mino in line):
                nb_lines_cleared += 1
                self.matrix.pop(y)
                self.matrix.append([None for x in range(NB_COLS)])    
        self.ui.update_matrix()
                
        if (
            self.current_piece.__class__ == Tetromino.T
            and self.current_piece.last_rotation_point_used is not None
        ):
            position = self.current_piece.position
            orientation = self.current_piece.orientation
            nb_orientations = len(self.current_piece.SRS[Rotation.CLOCKWISE])
            a = not self.cell_is_free(position+self.T_SLOT[orientation])
            b = not self.cell_is_free(position+self.T_SLOT[(orientation-1)%nb_orientations])
            c = not self.cell_is_free(position+self.T_SLOT[(orientation-3)%nb_orientations])
            d = not self.cell_is_free(position+self.T_SLOT[(orientation-2)%nb_orientations])
            
            if self.current_piece.last_rotation_point_used == 5 or (a and b and (c or d)):
                t_spin = T_Spin.T_SPIN
            elif c and d and (a or b):
                t_spin = T_Spin.MINI_T_SPIN
            else:
                t_spin = T_Spin.NO_T_SPIN
        else:
            t_spin = T_Spin.NO_T_SPIN
    
        if t_spin:
            self.ui.display(t_spin)
        if nb_lines_cleared:
            self.ui.display(self.SCORES[nb_lines_cleared]["name"])
            self.combo += 1
        else:
            self.combo = -1
            
        if nb_lines_cleared or t_spin:
            self.nb_lines += nb_lines_cleared
            ds = self.SCORES[nb_lines_cleared][t_spin]
            self.goal -= ds
            ds *= 100 * self.level
            self.score += ds
            self.ui.display(str(ds))
            
        if self.combo >= 1:
            self.ui.display("COMBO x%d" % self.combo)
            ds = (20 if nb_lines_cleared==1 else 50) * self.combo * self.level
            self.score += ds
            self.ui.display(str(ds))
            
        if self.score > self.high_score:
            self.high_score = self.score
        if self.goal <= 0:
            self.new_level()
            
        self.new_current_piece()

    def swap(self):
        if self.current_piece.hold_enabled:
            self.current_piece.hold_enabled = False
            self.current_piece.prelocked = False
            self.ui.cancel_prelock()
            self.ui.stop_fall()
            self.current_piece, self.held_piece = self.held_piece, self.current_piece
            if self.held_piece.__class__ == Tetromino.I:
                self.held_piece.position = HELD_I_POSITION
            else:
                self.held_piece.position = HELD_PIECE_POSITION
            self.held_piece.minoes_positions = self.held_piece.MINOES_POSITIONS
            self.ui.new_held_piece()
            if not self.current_piece:
                self.new_current_piece()
            else:
                self.current_piece.position = MATRIX_PIECE_INIT_POSITION
                self.ui.new_current_piece()
                self.ui.start_fall()
        
    def game_over(self):
        self.status = Status.OVER
        self.ui.game_over()
            

class UI(arcade.Window):
    
    def __init__(self):
        super().__init__(
            width = WINDOW_WIDTH,
            height = WINDOW_HEIGHT,
            title = WINDOW_TITLE,
            resizable = False
        )
        center_x = self.width / 2
        center_y = self.height / 2
        self.bg_sprite = arcade.Sprite(WINDOW_BG)
        self.bg_sprite.center_x = center_x
        self.bg_sprite.center_y = center_y
        self.matrix_minoes_sprites = arcade.SpriteList()
        self.held_piece_sprites = arcade.SpriteList()
        self.current_piece_sprites = arcade.SpriteList()
        self.ghost_piece_sprites = arcade.SpriteList()
        self.next_piece_sprites = arcade.SpriteList()
        self.matrix_sprite = arcade.Sprite(MATRIX_SPRITE_PATH)
        self.matrix_sprite.center_x = center_x
        self.matrix_sprite.center_y = center_y
        self.matrix_sprite.left = int(self.matrix_sprite.left)
        self.matrix_sprite.top = int(self.matrix_sprite.top)
        self.matrix_sprite.alpha = 100
        
        self.music = arcade.load_sound(MUSIC_PATH)
            
        self.actions = {
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
            }
        }
        self.autorepeatable_actions = (self.move_left, self.move_right, self.soft_drop)
        
        self.game = GameLogic(self)
        self.new_game()
        
    def new_game(self):
        self.pressed_actions = []
        self.auto_repeat = False
        arcade.play_sound(self.music)
        self.game.new_game()
    
    def display_new_level(self, level):
        print("Level", level)
        
    def new_piece(self, piece):
        piece_sprites = arcade.SpriteList()
        for mino_position in piece.minoes_positions:
            mino_sprite_path = MINOES_SPRITES_PATHS[piece.MINOES_COLOR]
            mino_sprite = arcade.Sprite(mino_sprite_path)
            mino_sprite.alpha = NORMAL_ALPHA
            piece_sprites.append(mino_sprite)
        return piece_sprites
        
    def new_held_piece(self):
        self.held_piece_sprites = self.new_piece(self.game.held_piece)
        self.update_held_piece()
        
    def new_next_piece(self):
        self.next_piece_sprites = self.new_piece(self.game.next_piece)
        self.update_next_piece()
        
    def new_current_piece(self):
        self.current_piece_sprites = self.new_piece(self.game.current_piece)
        self.ghost_piece_sprites = self.new_piece(self.game.ghost_piece)
        self.update_current_piece()
                
    def on_key_press(self, key, modifiers):
        for key_or_modifier in (key, modifiers):
            try:
                action = self.actions[self.game.status][key_or_modifier]
            except KeyError:
                pass
            else:
                action()
                if action in self.autorepeatable_actions:
                    self.stop_autorepeat()
                    self.pressed_actions.append(action)
                    arcade.schedule(self.repeat_action, AUTOREPEAT_DELAY)
            
    def on_key_release(self, key, modifiers):
        try:
            action = self.actions[self.game.status][key]
        except KeyError:
            pass
        else:
            if action in self.autorepeatable_actions:
                self.pressed_actions.remove(action)
                if not self.pressed_actions:
                    self.stop_autorepeat()
                    arcade.schedule(self.repeat_action, AUTOREPEAT_DELAY)
                    
    def repeat_action(self, delta_time=0):
        if self.pressed_actions:
            self.pressed_actions[-1]()
            if not self.auto_repeat:
                self.auto_repeat = True
                arcade.unschedule(self.repeat_action)
                arcade.schedule(self.repeat_action, AUTOREPEAT_INTERVAL)
        else:
            self.auto_repeat = False
            arcade.unschedule(self.repeat_action)
            
    def stop_autorepeat(self):
        self.auto_repeat = False
        arcade.unschedule(self.repeat_action)
        
    def move_left(self, delta_time=0):
        if self.game.move(Movement.LEFT):
            self.update_current_piece()
    
    def move_right(self, delta_time=0):
        if self.game.move(Movement.RIGHT):
            self.update_current_piece()
    
    def soft_drop(self, delta_time=0):
        if self.game.soft_drop():
            self.update_current_piece()
    
    def hard_drop(self, delta_time=0):
        self.game.hard_drop()
        self.lock()
    
    def rotate_counterclockwise(self, delta_time=0):
        if self.game.rotate(Rotation.COUNTERCLOCKWISE):
            self.update_current_piece()
    
    def rotate_clockwise(self, delta_time=0):
        if self.game.rotate(Rotation.CLOCKWISE):
            self.update_current_piece()
    
    def fall(self, delta_time=0):
        if self.game.move(Movement.DOWN):
            self.update_current_piece()
            
    def start_fall(self):
        arcade.schedule(self.fall, self.game.fall_delay)
            
    def stop_fall(self):
        arcade.unschedule(self.fall)
            
    def prelock(self, restart=False):
        if restart:
            self.cancel_prelock()
        arcade.schedule(self.lock, self.game.lock_delay)
        
    def cancel_prelock(self):
        arcade.unschedule(self.lock)
            
    def lock(self, delta_time=0):
        self.game.lock()
        
    def update_matrix(self):
        self.current_piece_sprites = arcade.SpriteList()
        self.matrix_minoes_sprites = arcade.SpriteList()
        for y, line in enumerate(self.game.matrix):
            for x, mino_color in enumerate(line):
                if mino_color:
                    mino_sprite_path = MINOES_SPRITES_PATHS[mino_color]
                    mino_sprite = arcade.Sprite(mino_sprite_path)
                    mino_sprite.left = self.matrix_sprite.left + x*(mino_sprite.width-1)
                    mino_sprite.bottom = self.matrix_sprite.bottom + y*(mino_sprite.height-1)
                    mino_sprite.alpha = 200
                    self.matrix_minoes_sprites.append(mino_sprite)
        
    def display(self, string):
        print(string)
        
    def swap(self, delta_time=0):
        self.game.swap()
        
    def pause(self, delta_time=0):
        print("pause")
        self.game.status = "paused"
        arcade.stop_sound(self.music)
        self.stop_fall()
        self.cancel_prelock()
        self.pressed_actions = []
        self.stop_autorepeat()
        
    def resume(self, delta_time=0):
        self.game.status = "playing"
        arcade.play_sound(self.music)
        self.start_fall()
        if self.game.current_piece.prelocked:
            arcade.schedule(self.lock, self.game.lock_delay)
        
    def on_draw(self):
        arcade.start_render()
        self.bg_sprite.draw()
        self.matrix_sprite.draw()
        if not self.game.status == "paused":
            self.matrix_minoes_sprites.draw()
            self.held_piece_sprites.draw()
            self.current_piece_sprites.draw()
            self.ghost_piece_sprites.draw()
            self.next_piece_sprites.draw()
            
    def update_piece(self, piece, piece_sprites):
        for mino_sprite, mino_position in zip(
            piece_sprites, piece.minoes_positions
        ):
            mino_position += piece.position
            mino_sprite.left = self.matrix_sprite.left + mino_position.x*(mino_sprite.width-1)
            mino_sprite.bottom = self.matrix_sprite.bottom + mino_position.y*(mino_sprite.height-1)
            
    def update_next_piece(self):
        self.update_piece(self.game.next_piece, self.next_piece_sprites)
            
    def update_held_piece(self):
        self.update_piece(self.game.held_piece, self.held_piece_sprites)
            
    def update_current_piece(self):
        self.update_piece(self.game.current_piece, self.current_piece_sprites)
        if self.game.current_piece.prelocked:
            alpha = PRELOCKED_ALPHA if self.game.current_piece.prelocked else NORMAL_ALPHA
            for mino_sprite in self.current_piece_sprites:
                mino_sprite.alpha = alpha
        self.update_piece(self.game.ghost_piece, self.ghost_piece_sprites)
        for mino_sprite in self.ghost_piece_sprites:
            mino_sprite.alpha = GHOST_ALPHA
            
    def game_over(self):
        arcade.unschedule(self.repeat_action)
        self.cancel_prelock()
        self.stop_fall()
        arcade.stop_sound(self.music)
        print("game over")

        
def main():
    UI()
    arcade.run()
    
if __name__ == "__main__":
    main()
    