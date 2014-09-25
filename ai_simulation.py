"""
Simulates an AI playing the game.
"""

import random

import cv2

from puyo.board import Puyo1Board
from puyo.ai import Puyo1DummyAI

def random_bean():
    return random.choice((b'r', b'g', b'b', b'y', b'p'))

def random_next_beans():
    return (random_bean(), random_bean())

def main():

    board = Puyo1Board(next_beans=random_next_beans())
    ai = Puyo1DummyAI()

    cv2.namedWindow("Puyo Board")
    while True:
        cv2.imshow("Puyo Board", board.draw())

        key = cv2.waitKey(-1) % 256

        if key == 27:  # Escape
            break
        elif key == ord(' '):

            if not board.is_game_over():
                current_beans = board.next_beans
                board.next_beans = random_next_beans()
                orientation, position = ai.move(board, current_beans)
                if board.can_make_move(orientation, position):
                    combo = board.make_move(current_beans, orientation, position)
                else:
                    print "Invalid Move:", orientation, position

            if board.is_game_over():
                print "Game Over"

if __name__ == "__main__":
    main()
