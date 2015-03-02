#!/usr/bin/python
"""
Simulates an AI playing the game.
"""

import random

import cv2

import puyo


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
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    ai_names = list(puyo.AI_REGISTRY.keys())
    parser.add_argument("-a", "--ai", choices=ai_names,
        default=puyo.DEFAULT_AI_NAME, help="AI to run. Choose one of: {} "
        "(default: {})".format(ai_names, puyo.DEFAULT_AI_NAME))
    parser.add_argument("-n", "--nuisance", type=float, default=0,
         dest="nuisance_probability", help="Probability (0-1) of a nuisance "
         "bean being dropped.")
    args = parser.parse_args()
    if args.nuisance_probability < 0 or args.nuisance_probability > 1:
        parser.error("Nuisance probability (-n, --nuisance) must be between "
            "0 and 1.")

    board = puyo.Board(next_beans=random_next_beans())
    ai = puyo.AI_REGISTRY[args.ai]()

    print("Keys:")
    print("  Space: Make move")
    print("  Escape: Quit")

    last_board = None
    game_over = False
    cv2.namedWindow("Puyo Board")
    while True:
        cv2.imshow("Puyo Board", board.draw())

        key = cv2.waitKey(-1) % 256

        if key == 27:  # Escape
            break

        elif key == ord(' '):

            if not game_over:
                last_board = board.copy()
                current_beans = board.next_beans
                board.next_beans = random_next_beans()
                position, rotation = ai.get_move(board.copy(), current_beans)
                #print current_beans, position, rotation
                if board.can_make_move(position, rotation):
                    combo = board.make_move(current_beans, position, rotation)
                    if combo.game_over:
                        print "Game Over"
                        game_over = True
                    print_combo(combo)
                else:
                    print "Invalid Move:", position, rotation

                if random.uniform(0, 1) < args.nuisance_probability:
                    board.drop_nuisance(1)

            if game_over:
                print "Game Over"

        elif key == ord('u'):
            board = last_board
            game_over = False

if __name__ == "__main__":
    main()
