"""
Recognizes and reconstructs a Puyo 1 board from a video stream.
"""

import pickle
import time

import cv2

from puyo import BeanFinder

def open_video(source):
    video = cv2.VideoCapture(source)

    if not video.isOpened():
        try:
            integer = int(source)
        except ValueError:
            pass
        else:
            video = cv2.VideoCapture(integer)

    if not video.isOpened():
        return None
    return video

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Video source filename or camera index")
    parser.add_argument("--player1", "-1", dest="player", const=1,
        action="store_const", help="Play as player 1. Reads the left side of "
        "the screen. (default)", default=1)
    parser.add_argument("--player2", "-2", dest="player", const=2,
        action="store_const", help="Play as player 2. Reads the right side "
        "of the screen.")
    parser.add_argument("--output", "-o", default=None,
        help="Record list of (board, timestamp) tuples to a pickle file.")

    args = parser.parse_args()

    video = open_video(args.source)
    if not video:
        print("Cannot open video stream")
        import sys
        sys.exit(1)

    #TODO: Make screen offset configurable
    bean_finder = BeanFinder((38, 13), args.player)
    cv2.namedWindow("Frame")
    cv2.namedWindow("Grid")

    board_data = []
    last_board = None
    start_time = None
    while True:

        was_read, img = video.read()
        if not was_read:
            print("Error: Could not read video frame!")
            if cv2.waitKey(-1) % 256:
                break
            continue
        cv2.imshow("Frame", img)

        board = bean_finder.get_board(img)
        cv2.imshow("Grid", board.draw())

        # Append to board_data
        if args.output is not None:
            t = time.time()
            if start_time is None:
                start_time = t
            if last_board is not None and board == last_board:
                b = None
            else:
                b = board
            board_data.append((b, t - start_time))

        key = cv2.waitKey(10) % 256
        if key == 27:  # Escape
            break

        last_board = board

    if args.output is not None:
        pickle.dump(board_data, open(args.output, 'wb'))


if __name__ == "__main__":
    main()
