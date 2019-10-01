# -*- coding: utf-8 -*-

from TetrArcade import TetrArcade, tetrislogic

game = TetrArcade()
game.new_game()
game.move_left()
game.move_right()
game.rotate_clockwise()
game.rotate_counter()
for i in range(12):
    game.soft_drop()
game.on_draw()
while game.state != tetrislogic.State.OVER:
    game.hard_drop()
