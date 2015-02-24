#!/usr/bin/python

import sys
import pickle

import cv2


def main():
    data = pickle.load(open(sys.argv[1], 'rb'))

    cv2.namedWindow("Grid")

    last_board = None
    for board, t in data:
        if board is None:
            board = last_board

        cv2.imshow("Grid", board.draw())

        key = cv2.waitKey(50) % 256
        if key == 27:  # Escape
            break

        last_board = board


if __name__ == "__main__":
    main()
