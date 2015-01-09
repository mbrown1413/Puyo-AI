
import unittest

import puyo


class TestPuyoBoard(unittest.TestCase):

    def make_board(self, positions, colors):
        b = puyo.PuyoBoard()
        assert len(positions) == len(colors)
        b.drop_beans(positions, colors)
        return b

    def test_can_make_move(self):
        """Many test vectors for `can_make_move` method."""
        # Each test vector is a tuple of:
        #
        #     ((positions, colors), position, rotation, expected result)
        #
        # First, beans are dropped at the corresponding bean positions with
        # the given colors given in the first item of the tuple. Then
        # `PuyoBoard.can_make_move()` is called with the position and rotation
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
            board = self.make_board(positions, colors)

            result = board.can_make_move(pos, rot)
            self.assertEqual(result, expected_result,
                "Test vector {} ({}) did not match expected result.".format(i, vector)
            )

    @unittest.skip("Test not written")
    def test_mechanics_combo1(self):
        """Test `make_move` method with a length 1 combo."""
        raise NotImplementedError()

    @unittest.skip("Test not written")
    def test_mechanics_combo2(self):
        """Test `make_move` method with a length 2 combo."""
        raise NotImplementedError()

    @unittest.skip("Test not written")
    def test_mechanics_of_nuisance(self):
        """Test `make_move` method when nuisance beans are present."""
        # Four nuisance beans should not make a combo
        # Nuisance beans should be eliminated when next to a combo
        # ...but not diagonally
        raise NotImplementedError()

    @unittest.skip("Test not written")
    def test_scoring(self):
        """`make_move` method should return correct score and combo info."""
        raise NotImplementedError()


if __name__ == "__main__":
    unittest.main()
