"""
A simple interface for testing the Puyo1Board class.

Keys:
    r g b y p k - Select red, green, blue, yellow, purple or black (nussance)
    1 2 3 4 5 6 - Drop a bean in this column.
    u - Undo (only one undo level)
    Esc - Quit
"""

import cv2

from puyo.board import Puyo1Board

COLOR_STRINGS = {
    b'r': "Red",
    b'g': "Green",
    b'b': "Blue",
    b'y': "Yellow",
    b'p': "Purple",
    b'k': "Black (nussance)",
}

def main():
    board = Puyo1Board()

    print __doc__

    current_color = None
    last_board = None
    cv2.namedWindow("Puyo Board")
    while True:
        cv2.imshow("Puyo Board", board.draw())

        key = cv2.waitKey(-1) % 256

        if key == 27:  # Escape
            break
        elif chr(key).lower() in COLOR_STRINGS:
            current_color = chr(key)
            print "Selected", COLOR_STRINGS[current_color]
        elif key >= ord('1') and key <= ord('6'):
            if current_color is not None:
                last_board = board.copy()
                board.drop_beans([int(chr(key))-1], [current_color])
            else:
                print "No color selected. Select using r, g, b, y, p or k."
        elif key == ord('u'):
            if last_board is not None:
                board = last_board
                last_board = None
                print "Undo Performed"
            else:
                print "Nothing to undo to!"

if __name__ == "__main__":
    main()
