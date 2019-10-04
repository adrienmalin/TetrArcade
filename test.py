# -*- coding: utf-8 -*-

from TetrArcade import TetrArcade, State, MinoSprite
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
game.swap()
game.rotate_clockwise()
game.rotate_counter()
for i in range(12):
    game.soft_drop()
game.matrix.sprites.refresh()
game.on_draw()
while game.state != State.OVER:
    game.hard_drop()
