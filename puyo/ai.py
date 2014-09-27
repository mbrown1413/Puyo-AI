
import random
import itertools

class PuyoAI(object):

    def move(self, board, beans):
        """Return a move as an (orientation, position) tuple.

        The given pair of beans are the current beans that are dropping.
        `board.next_beans` will be the pair after that, or None if it's
        unknown.

        """
        raise NotImplementedError("This method must be implemented by a "
                                  "subclass.")


class Puyo1DummyAI(PuyoAI):
    """AI that makes completely random moves."""

    def move(self, board, beans):
        possible_moves = board.iter_moves()
        return random.choice(list(possible_moves))


class ScoreBasedAI(PuyoAI):

    def move(self, board, beans):
        score_func = lambda move: self.score_move(board, beans, *move)
        moves = list(board.iter_moves())
        random.shuffle(moves)
        move = max(moves, key=score_func)
        #print score_func(move)
        return move

    def score_move(self, board, beans, orientation, position):
        raise NotImplementedError("This method must be implemented by a "
                                  "subclass.")


class SimpleGreedyAI(ScoreBasedAI):
    """Very, very greedy.

    Scores each move by how many connected beans there are. Each group adds the
    square of the group size to that move's score (so a group of 1 counts as 1,
    and a group of 3 counts as 9). If any moves eliminate pieces, the one with
    the highest score is chosen. Ties are broken randomly.

    """

    def score_move(self, board, beans, orientation, position):
        board = board.copy()
        combo = board.make_move(beans, orientation, position)
        value = 0

        if combo.n_beans:
            value += combo.score

        for x in range(6):
            for y in range(12):
                value += len(board.get_connected(x, y))

        return value


class SimpleComboAI(ScoreBasedAI):

    def score_move(self, board, beans, orientation, position):
        board = board.copy()
        combo = board.make_move(beans, orientation, position)
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
