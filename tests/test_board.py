#!/usr/bin/python

import unittest

import puyo

from helper import PuyoTestCase


class TestBoard(PuyoTestCase):

    def make_board(self, *args, **kwargs):
        return puyo.Board(*args, c_accelerated=False, **kwargs)

    def make_board_from_drops(self, positions=(), colors=()):
        b = self.make_board()
        assert len(positions) == len(colors)
        b.drop_beans(positions, colors)
        return b

    def board_from_strs(self, rows, next_beans=None):

        for i in range(12-len(rows)):
            rows.insert(0, b"      ")

        board = [[rows[11-y][x] for y in range(12)]
                                for x in range(6)]
        return self.make_board(board, next_beans)

    def test_board_mutation(self):
        board = self.make_board()
        self.assertEquals(board[1][1], b' ')

        board[1][1] = b'r'
        self.assertEquals(board[1][1], b'r')
        self.assertEquals(board[1, 1], b'r')

        board2 = board.copy()

        board[1,1] = b'g'
        self.assertEquals(board[1][1], b'g')
        self.assertEquals(board[1, 1], b'g')

        self.assertEquals(board2[1][1], b'r')
        self.assertEquals(board2[1, 1], b'r')

    def test_can_make_move(self):
        """Many test vectors for `can_make_move` method."""
        # Each test vector is a tuple of:
        #
        #     ((positions, colors), position, rotation, expected result)
        #
        # First, beans are dropped at the corresponding bean positions with
        # the given colors given in the first item of the tuple. Then
        # `Board.can_make_move()` is called with the position and rotation
        # given. The expected result is then compared with the actual result.
        tests = []

        # Nothing filled, every move should work
        b = [], []
        tests.extend([(b, pos, rot, True) for pos in range(5)
                                          for rot in range(4)])
        tests.extend([(b, 5, rot, True) for rot in (0, 2)])

        # First column filled up
        b = [0]*12, [b'r', b'g']*6
        tests.extend([
            (b, 0, 0, False),
            (b, 0, 1, False),
            (b, 0, 2, False),
            (b, 0, 3, False),
            (b, 1, 0, True),
            (b, 1, 1, True),
            (b, 1, 2, True),
            (b, 1, 3, True),
        ])

        # One empty space in first column
        b = [0]*11, [[b'r', b'g'][i%2] for i in range(11)]
        tests.extend([
            (b, 0, 0, True),
            (b, 0, 1, True),
            (b, 0, 2, True),
            (b, 0, 3, True),
        ])

        # First column blocked off by second
        b = [1]*12, [b'r', b'g']*6
        tests.extend([(b, 0, r, False) for r in range(4)])
        tests.extend([(b, 1, r, False) for r in range(4)])
        tests.extend([(b, 2, r, True) for r in range(4)])

        # Sixth column blocked off by fifth
        b = [4]*12, [b'r', b'g']*6
        tests.extend([(b, 5, r, False) for r in (0, 2)])
        tests.extend([(b, 4, r, False) for r in range(4)])
        tests.extend([(b, 3, r, r%2 == 0) for r in range(4)])

        # No room to rotate when starting pos is surrounded by filled columns
        b = [1]*12 + [3]*12, [b'r', b'g']*12
        tests.extend([
            (b, 2, 0, True),
            (b, 2, 1, False),
            (b, 2, 2, False),
            (b, 2, 3, False),
        ])

        for i, vector in enumerate(tests):
            beans, pos, rot, expected_result = vector

            positions, colors = beans
            board = self.make_board_from_drops(positions, colors)

            result = board.can_make_move(pos, rot)
            self.assertEqual(result, expected_result,
                "Test vector {} ({}) did not match expected result.".format(i, vector)
            )

    def test_combo1(self):
        """Simple length 1 combo mechanics."""
        board = self.board_from_strs([
            b"rr r  ",
        ])
        combo = board.drop_bean(2, b'r')
        self.assertEquals(combo.score, 40)
        self.assertEquals(combo.n_beans, 4)
        self.assertEquals(combo.length, 1)
        self.assertBoardEmpty(board)

    def test_combo2(self):
        """Simple length 1 combo mechanics."""
        board = self.board_from_strs([
            b"   r  ",
            b"rrrggg",
        ])
        combo = board.drop_bean(5, b'g')
        self.assertEquals(combo.score, 360)
        self.assertEquals(combo.n_beans, 8)
        self.assertEquals(combo.length, 2)
        self.assertBoardEmpty(board)

    def test_nuisance_elimination(self):
        """Nuisance beans should be eliminated when next to a combo."""
        board = self.board_from_strs([
            b"rr rk ",
        ])
        combo = board.drop_bean(2, b'r')
        self.assertEquals(combo.score, 40)
        self.assertEquals(combo.n_beans, 4)
        self.assertEquals(combo.length, 1)
        self.assertBoardEmpty(board)

    def test_nuisance_no_combo(self):
        """Four nuisance beans should not make a combo."""
        board = self.board_from_strs([
            b"kk    ",
            b"kk    ",
        ])
        combo = board.drop_bean(2, b'g')
        self.assertEquals(combo.score, 0)
        self.assertEquals(combo.n_beans, 0)
        self.assertEquals(combo.length, 0)
        self.assertBoardEquals(board, self.board_from_strs([
            b"kk    ",
            b"kkg   ",
        ]))

    def test_nuisance_no_combo_diagonal(self):
        """Nuisance beans not should be eliminated when diagonal to a combo."""
        board = self.board_from_strs([
            b"    k ",
            b"rr rg ",
        ])
        combo = board.drop_bean(2, b'r')
        self.assertBoardEquals(board, self.board_from_strs([
            b"    k ",
            b"    g ",
        ]))

    def test_long_combo(self):
        """Chain length 18!"""
        board = self.board_from_strs([
            b" pyybg",
            b"bbppyg",
            b"bpyrbb",
            b"ygprpb",
            b"gprpgg",
            b"gbprpr",
            b"gypypb",
            b"ybbbyy",
            b"yrgrgy",
            b"rgrgrb",
            b"rgrgrb",
            b"rgrgrb",
        ])

        # Make sure nothing eliminates prematurely
        combo = board.drop_beans([], [])
        self.assertEquals(combo.length, 0)

        combo = board.drop_bean(0, b'b')
        self.assertEquals(combo.n_beans, 6*12)
        self.assertEquals(combo.length, 18)
        self.assertBoardEmpty(board)

        # This score value is Puyo Puyo 1 specific. The value will not match
        # up with the usual online chain simulator
        # (http://puyonexus.net/chainsim/) because the chain power table is
        # different for Puyo 1.
        self.assertEquals(combo.score, 440280)  # This is a puyo puyo (1)

    def test_drop_nuisance_1(self):
        board = self.make_board()
        board.drop_nuisance(1)
        self.assertEqual(board.count(b'k'), 1)

    def test_drop_nuisance_6(self):
        board = self.make_board()
        board.drop_nuisance(6)
        self.assertBoardEquals(board, self.board_from_strs([b'kkkkkk']))

    def test_drop_nuisance_7(self):
        board = self.make_board()
        board.drop_nuisance(7)
        self.assertEqual(board.count(b'k'), 7)
        for x in range(6):
            self.assertEqual(board[x][0], b'k')

    def test_drop_nuisance_36(self):
        board = self.make_board()
        board.drop_nuisance(36)
        self.assertBoardEquals(board, self.board_from_strs([b'kkkkkk']*6))

    def test_drop_nuisance_73(self):
        """Nuisance beans dropped over the top should be ignored."""
        board = self.make_board()
        board.drop_nuisance(73)
        self.assertBoardEquals(board, self.board_from_strs([b'kkkkkk']*12))


class TestBoardCAccelerated(TestBoard):
    """Test `puyo.Board` with C acceleration."""

    def make_board(self, *args, **kwargs):
        board = puyo.Board(*args, c_accelerated=True, **kwargs)
        if not board.c_accelerated:
            raise RuntimeError("C acceleration not available, cannot test it.")
        return board


if __name__ == "__main__":
    unittest.main()
