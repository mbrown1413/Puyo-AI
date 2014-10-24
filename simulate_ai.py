"""
Simulates an AI playing the game.
"""

import random

import cv2

from puyo.board import PuyoBoard
from puyo.ai import SimpleComboAI

def random_bean():
    return random.choice((b'r', b'g', b'b', b'y', b'p'))

def random_next_beans():
    return (random_bean(), random_bean())

def print_combo(combo):
    if not combo.length:
        return

    print "score={} n_beans={}".format(combo.score, combo.n_beans),
    if combo.length > 1:
        print "length={}".format(combo.length)
    else:
        print

def main():

    board = PuyoBoard(next_beans=random_next_beans())
    ai = SimpleComboAI()

    cv2.namedWindow("Puyo Board")
    while True:
        cv2.imshow("Puyo Board", board.draw())

        key = cv2.waitKey(-1) % 256

        if key == 27:  # Escape
            break

        elif key == ord(' '):

            if not board.is_game_over():
                last_board = board.copy()
                current_beans = board.next_beans
                board.next_beans = random_next_beans()
                position, rotation = ai.move(board, current_beans)
                #print current_beans, position, rotation
                if board.can_make_move(position, rotation):
                    combo = board.make_move(current_beans, position, rotation)
                    print_combo(combo)
                else:
                    print "Invalid Move:", position, rotation
                #if random.randint(0, 9) > 6:
                #    board.drop_black_bean(random.randint(0, 5))

            if board.is_game_over():
                print "Game Over"

        elif key == ord('u'):
            board = last_board

if __name__ == "__main__":
    main()
