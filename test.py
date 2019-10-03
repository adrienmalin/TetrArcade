# -*- coding: utf-8 -*-

from TetrArcade import TetrArcade, State

game = TetrArcade()
game.new_game()
game.move_left()
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
