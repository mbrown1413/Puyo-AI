"""PuyoAI and subclasses, which determine what moves to make in a Puyo game.

All AIs subclass from the PuyoAI class and define a `get_move` method that
determines the next move that is made. To make an AI available, add it to
`puyo.AI_REGISTRY` defined in "puyo/__init__.py".

"""

import random
import itertools


class PuyoAI(object):
    """Abstract base AI class."""

    def get_move(self, board, beans):
        """Determine the next move to make.

        Args:
            board: The current state of the game as a PuyoBoard object.
                `board.next_beans` is a pair of beans that represents not the
                current beans that are dropping, but the next pair that will
                drop, or None if it is unknown.
            beans: The current pair of beans that are dropping. The return
                value will determine where these beans go.

        Returns:
            A move as a `(position, rotation)` tuple. See the docs for
            `puyo.PuyoBoard.make_move()` for exactly how moves are defined by a
            position and rotation.

        Note that the user of a PuyoAI subclass is allowed to call this
        function without actually performing the returned move. Don't keep
        state from one call to the next that makes this assumption.

        """
        raise NotImplementedError("This method must be implemented by a "
                                  "subclass.")


class RandomAI(PuyoAI):
    """AI that makes completely random moves."""

    def get_move(self, board, beans):
        possible_moves = board.iter_moves()
        return random.choice(list(possible_moves))


class ScoreBasedAI(PuyoAI):
    """Abstract class for a PuyoAI that works by scoring each possible move."""

    def get_move(self, board, beans):
        score_func = lambda move: self.score_move(board, beans, *move)
        moves = list(board.iter_moves())
        random.shuffle(moves)  # Select randomly between ties
        move = max(moves, key=score_func)
        return move

    def score_move(self, board, beans, pos, rot):
        """Return a score for a particular move.

        Args:
            board, beans: Same as `get_move`.
            pos, rot: A possible return value for `get_move`. Note that the move
                has not yet been applied to the board passed to this method.

        Returns:
            A score as a float or int. The greatest scored move will be chosen
            and returned by `get_move`, with ties broken randomly.

        """
        raise NotImplementedError("This method must be implemented by a "
                                  "subclass.")


class SimpleGreedyAI(ScoreBasedAI):
    """Very, very greedy.

    Scores each move by how many connected beans there are. Each group adds the
    square of the group size to that move's score (so a group of 1 counts as 1,
    and a group of 3 counts as 9). If any moves eliminate pieces, the one with
    the highest score is chosen. Ties are broken randomly.

    """

    def score_move(self, board, beans, pos, rot):
        board = board.copy()
        combo = board.make_move(beans, pos, rot)
        value = 0

        if combo.n_beans:
            value += combo.score

        for x in range(6):
            for y in range(12):
                value += len(board.get_connected(x, y))

        # Don't give yourself a game over
        if board.board[2][11] != b' ':
            value = 0

        return value


class SimpleComboAI(ScoreBasedAI):
    """
    Like the SimpleGreedyAI, but it values moves more when they have the
    potential to make combos.
    """

    def score_move(self, board, beans, pos, rot):
        board = board.copy()
        combo = board.make_move(beans, pos, rot)
        value = 0

        for color in (b'r', b'g', b'b', b'y', b'p'):
            for x in range(6):
                tmp_combo = board.copy().drop_beans([x], [color])
                if tmp_combo.length >= 2:
                    value += tmp_combo.score

        if combo.length < 2:
            value -= combo.score
        elif combo.length > 2:
            value += 2*combo.score

        for x in range(6):
            for y in range(12):
                value += len(board.get_connected(x, y))

        # Don't give yourself a game over
        if board.board[2][11] != b' ':
            value = 0

        return value
