
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
    Board recording pickle files contain a list of (cells, next_beans, time)
    tuples. `cells` and `next_beans` define the current state of the board. If
    `cells` or `next_beans` is None, they are assumed to be the same as the
    previous. Time is measured relatively in seconds.
    """
    filename = os.path.join(TEST_DATA_FOLDER, filename)
    data = pickle.load(open(filename))
    last_cells = None
    last_next_beans = None
    for cells, next_beans, t in data:

        if cells is None:
            cells = last_cells
        if next_beans is None:
            next_beans = last_next_beans

        yield puyo.Board(cells, next_beans), t

        last_cells = cells
        last_next_beans = next_beans


class PuyoTestCase(unittest.TestCase):

    def assertBoardEquals(self, board1, board2):
        self.assertEquals(board1.board.tolist(), board2.board.tolist())
        self.assertEquals(board1.next_beans, board2.next_beans)

    def assertBoardEmpty(self, board):
        self.assertBoardEquals(board, board_from_strs([]))
