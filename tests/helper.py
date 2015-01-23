
import os
import unittest
import pickle

import puyo


TEST_DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")


def board_from_strs(rows, next_beans=None):

    for i in range(12-len(rows)):
        rows.insert(0, b"      ")

    board = [[rows[11-y][x] for y in range(12)]
                            for x in range(6)]
    return puyo.Board(board, next_beans)


def read_board_recording(filename):
    """
    Board recording pickle files contain a list of (board, time) pairs. If
    board is None, it is assumed to be the same as the previous board. Time is
    measured relatively in seconds.
    """
    filename = os.path.join(TEST_DATA_FOLDER, filename)
    data = pickle.load(open(filename))
    last_board = None
    for board, t in data:
        if board is None:
            board = last_board
        else:
            last_board = board
        yield board, t


class PuyoTestCase(unittest.TestCase):

    def assertBoardEquals(self, board1, board2):
        self.assertEquals(board1.board.tolist(), board2.board.tolist())
        self.assertEquals(board1.next_beans, board2.next_beans)

    def assertBoardEmpty(self, board):
        self.assertBoardEquals(board, board_from_strs([]))
