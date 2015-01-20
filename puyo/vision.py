
from collections import namedtuple
from time import time

from puyo import BeanFinder


MIN_NEW_MOVE_WAIT_TIME = 0.3


# The state of a single player's half of the game.
#
# Items:
#   board: The current board state as a Board object.
#   new_move: Did a bean just start dropping? True of False
PlayerState = namedtuple("PlayerState", "board new_move current_beans")


class Vision(object):
    """Keeps track of the game state of a single player over time.

    Internally, the `BeanFinder` class is used to get the state of each frame.
    Since this class is stateful, it can provide extra information, such as
    when a new move begins. This extra state is also used for inter-frame error
    correction.

    """

    def __init__(self, bean_finder=None, player=None, timing_scheme="absolute"):
        """
        Args:
            bean_finder: A `BeanFinder` instance, or None if one should be
                automatically created.
            player: If `bean_finder` is None, this is used to construct a
                `BeanFinder` object with the intended player. If `bean_finder`
                is given, this argument should be None (default).
            timing_scheme: "relative" or "absolute". If "relative", `dt` must
                be given to each call of `get_state`, otherwise `dt` cannot be
                given.
        """
        if bean_finder is None:
            assert player in (None, 1, 2)
            if player is None:
                player = 1
            bean_finder = BeanFinder((38, 13), player)
        else:
            assert player is None
        self.bean_finder = bean_finder

        if timing_scheme == "relative":
            self.relative_timing = True
            self.prev_time = float('-inf')
            self.current_time = 0
        elif timing_scheme == "absolute":
            self.relative_timing = False
            self.prev_time = float('-inf')
            self.current_time = float('-inf')
        else:
            raise ValueError('`timing_scheme` must be "relative" or "absolute"')

        self.old_board = None  # Board from the previous frame
        self.next_beans = None  # Beans next to fall
        self.current_beans = None  # Beans currently falling
        self.beans_falling = False
        self.last_new_move_time = float('-inf')

    def get_state(self, img, dt=None):
        """Return a PlayerState object representing the current player state.

        Args:
            img: Current video frame of the game.
            dt: The time, in seconds, since the last image given to
                `set_state`. If `timing_scheme` was set to "absolute" this
                parameter cannot be used. If `timing_scheme is "relative", it
                must be used.

        Returns: PlayerState object representing the state of the player's half
            of the game

        """
        if self.relative_timing:
            assert dt is not None
            self.prev_time, self.current_time = self.current_time, self.current_time + dt
        else:
            assert dt is None
            self.prev_time, self.current_time = self.current_time, time()

        board = self.bean_finder.get_board(img)

        if self.next_beans is None:
            self.next_beans = board.next_beans

        for x in range(0, 6):
            for y in range(1, 12):
                if x == 2 and (y == 11 or y == 10):
                    continue
                if board.board[x][y] != b' ' and board.board[x][y-1] == b' ':
                    return PlayerState(board, False, self.current_beans)

        board, new_move = self._is_new_move(self.old_board, board)

        if new_move and self.current_time - self.last_new_move_time < MIN_NEW_MOVE_WAIT_TIME:
            new_move = False

        if new_move:
            self.current_beans = self.next_beans
            self.next_beans = board.next_beans
            self.beans_falling = True
            self.last_new_move_time = self.current_time

        self.old_board = board
        return PlayerState(board, new_move, self.current_beans)

    def _is_new_move(self, old_board, new_board):

        # Check if next_beans has changed
        if new_board.next_beans is not None and \
                self.next_beans is not None and \
                self.next_beans != new_board.next_beans:

            if old_board.board[2][11] == b' ':
                new_board.board[2][11] = b' '
            return new_board, True

        if self.beans_falling:
            if new_board.board[2][11] == b' ':
                self.beans_falling = False

        else:

            # Check if bean is falling
            # We need to look for the beans falling in the third column, in
            # case the next bean happens to be the same as the current. It
            # happens more often than you'd think!
            if old_board is not None and self.next_beans is not None:
                if (old_board.board[2][11] in (b' ', b'k') and
                    new_board.board[2][11] == self.next_beans[1]):

                        new_board.board[2][11] = b' '
                        return new_board, True

                elif (old_board.board[2][11] in (b' ', b'k') and
                    old_board.board[2][10] in (b' ', b'k') and
                    new_board.board[2][11] == self.next_beans[0] and
                    new_board.board[2][10] == self.next_beans[1]):

                        new_board.board[2][11] = b' '
                        new_board.board[2][10] = b' '
                        return new_board, True

        return new_board, False
