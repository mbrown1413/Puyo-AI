
import os
import unittest

import cv2

import puyo


TEST_IMG_FOLDER = os.path.join(os.path.dirname(__file__), "img")


def board_from_strs(rows, next_beans=None):

    for i in range(12-len(rows)):
        rows.insert(0, b"      ")

    board = [[rows[11-y][x] for y in range(12)]
                            for x in range(6)]
    return puyo.Board(board, next_beans)


class TestBeanFinder(unittest.TestCase):

    def assertBoardEquals(self, board1, board2):
        self.assertEquals(board1.board.tolist(), board2.board.tolist())
        self.assertEquals(board1.next_beans, board2.next_beans)

    def assertImageMatchesBoard(self, img_filename, board):
        bean_finder = puyo.BeanFinder((38, 13), 1)
        img = cv2.imread(os.path.join(TEST_IMG_FOLDER, img_filename))
        if img is None:
            raise OSError("Image not found")
        recognized_board = bean_finder.get_board(img)
        self.assertBoardEquals(board, recognized_board)

    def test_recognition_1(self):
        """Simple image with no nussance beans."""
        board = board_from_strs([
            b"r     ",
            b"r     ",
            b"g     ",
            b"p g g ",
            b"r p y ",
            b"yprrb ",
            b"ppypyr",
            b"yygbbr",
            b"rbpryp",
        ], next_beans=(b'p', b'y'))
        self.assertImageMatchesBoard("beanfinder_1.png", board)

    def test_recognition_2(self):
        """
        More complex image with nussance beans and sweat from the monkey
        obscuring some beans.
        """
        board = board_from_strs([
            b"bb    ",
            b"rp    ",
            b"rr    ",
            b"pp  b ",
            b"rp  y ",
            b"pb  k ",
            b"kkr gk",
            b"rgbbyy",
            b"rgbryk",
            b"rprrgg",
            b"bbbyyp",
            b"rgpypg",
        ], next_beans=(b'b', b'p'))
        self.assertImageMatchesBoard("beanfinder_2.png", board)

    def test_yellow_similar_to_green(self):
        """
        This is a test image where x=2 y=5 sometimes gets counted as green,
        instead of yellow.
        """
        board = board_from_strs([
            b"  y   ",
            b"  y   ",
            b"  y   ",
            b"y g   ",
            b"g ggp ",
            b"r ypr ",
            b"rryyrg",
            b"gypryg",
        ], next_beans=(b'p', b'y'))
        self.assertImageMatchesBoard("beanfinder_yellow_similar_to_green.png", board)


if __name__ == "__main__":
    unittest.main()
