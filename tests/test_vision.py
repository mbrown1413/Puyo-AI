
import unittest

import puyo


class MockBeanFinder(puyo.BeanFinder):
    """
    A mock puyo.BeanFinder class. Instead of `get_board()` taking an image as
    an argument, it takes a PuyoBoard object which it simply returns.
    """

    def __init__(self):
        pass

    def get_board(self, board):
        return board


class TestPuyoVision(unittest.TestCase):

    def test_new_move_on_next_bean_change(self):
        """New move should be detected when the next bean changes."""
        pv = puyo.PuyoVision(bean_finder=MockBeanFinder())
        board1 = puyo.PuyoBoard(next_beans=(b'r', b'g'))
        board2 = puyo.PuyoBoard(next_beans=(b'b', b'g'))

        state = pv.get_state(board1, 5)
        self.assertFalse(state.new_move)

        # Change in next bean
        state = pv.get_state(board2, 5)
        self.assertTrue(state.new_move)

        # No change
        state = pv.get_state(board2, 5)
        self.assertFalse(state.new_move)

        # Change
        state = pv.get_state(board1, 5)
        self.assertTrue(state.new_move)

    @unittest.expectedFailure
    def test_new_move_on_seen_falling1(self):
        """New move should be detected when new beans are seen falling."""
        pv = puyo.PuyoVision(bean_finder=MockBeanFinder())
        board1 = puyo.PuyoBoard(next_beans=(b'r', b'g'))

        state = pv.get_state(board1, 5)
        self.assertFalse(state.new_move)

        # Seeing green should trigger a new move
        board2 = board1.copy()
        board2.board[2][11] = b'g'
        state = pv.get_state(board2, 5)
        self.assertTrue(state.new_move)

        # Seeing another should not trigger a new move
        state = pv.get_state(board2, 5)
        self.assertFalse(state.new_move)

    @unittest.expectedFailure
    def test_new_move_on_seen_falling2(self):
        """New move should be detected when new beans are seen falling."""
        pv = puyo.PuyoVision(bean_finder=MockBeanFinder())
        board1 = puyo.PuyoBoard(next_beans=(b'r', b'g'))

        state = pv.get_state(board1, 5)
        self.assertFalse(state.new_move)

        # Seeing red and green in the correct order should trigger a new move
        board2 = board1.copy()
        board2.board[2][11] = b'r'
        board2.board[2][10] = b'g'
        state = pv.get_state(board2, 5)
        self.assertTrue(state.new_move)

        # Seeing another should not trigger a new move
        state = pv.get_state(board2, 5)
        self.assertFalse(state.new_move)

    def test_no_new_move_on_wrong_colors(self):
        """No new move should be detected when colors don't match the next bean."""
        pv = puyo.PuyoVision(bean_finder=MockBeanFinder())
        board = puyo.PuyoBoard(next_beans=(b'r', b'g'))

        state = pv.get_state(board, 5)
        self.assertFalse(state.new_move)

        # Yellow bean should not trigger new move
        tmp_board = board.copy()
        tmp_board.board[2][11] = b'y'
        state = pv.get_state(tmp_board, 5)
        self.assertFalse(state.new_move)

        # Neither should red alone, since green falls first
        tmp_board = board.copy()
        tmp_board.board[2][11] = b'r'
        state = pv.get_state(tmp_board, 5)
        self.assertFalse(state.new_move)

        # Neither should green then red, since red should be on top
        tmp_board = board.copy()
        tmp_board.board[2][11] = b'g'
        tmp_board.board[2][10] = b'r'
        state = pv.get_state(tmp_board, 5)
        self.assertFalse(state.new_move)

    def test_no_new_move_on_wrong_column(self):
        """No new move should be detected when beans falling in the wrong column."""
        pv = puyo.PuyoVision(bean_finder=MockBeanFinder())
        board1 = puyo.PuyoBoard(next_beans=(b'g', b'g'))

        state = pv.get_state(board1, 5)
        self.assertFalse(state.new_move)

        board2 = board1.copy()
        board2.board[3][11] = b'g'
        state = pv.get_state(board2, 5)
        self.assertFalse(state.new_move)


if __name__ == "__main__":
    unittest.main()
