
import unittest

import puyo


def board_from_strs(rows, next_beans=None):

    for i in range(12-len(rows)):
        rows.insert(0, b"      ")

    board = [[rows[11-y][x] for y in range(12)]
                            for x in range(6)]
    return puyo.Board(board, next_beans)


class PuyoTestCase(unittest.TestCase):

    def assertBoardEquals(self, board1, board2):
        self.assertEquals(board1.board.tolist(), board2.board.tolist())
        self.assertEquals(board1.next_beans, board2.next_beans)

    def assertBoardEmpty(self, board):
        self.assertBoardEquals(board, board_from_strs([]))
