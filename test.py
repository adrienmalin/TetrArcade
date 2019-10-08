# -*- coding: utf-8 -*-

from TetrArcade import TetrArcade, MinoSprite, State
from tetrislogic import Mino, Color, Coord

game = TetrArcade()
game.new_game()
for x in range(game.matrix.collumns):
    mino = Mino(Color.ORANGE, Coord(x, 0))
    mino.sprite = MinoSprite(mino, game, 200)
    game.matrix[0][x] = mino
    game.matrix.sprites.append(mino.sprite)
game.move_left()
game.pause()
game.resume()
game.move_right()
game.hold()
game.update(0)
game.on_draw()
game.rotate_clockwise()
game.hold()
game.update(0)
game.on_draw()
game.rotate_counter()
for i in range(22):
    game.soft_drop()
    game.on_draw()
game.lock_phase()
game.hold()
game.update(0)
game.on_draw()
while game.state != State.OVER:
    game.hard_drop()
game.on_draw()
