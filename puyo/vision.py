
from collections import namedtuple

from puyo import BeanFinder


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

    def __init__(self, bean_finder=None, player=None):
        """
        Args:
            bean_finder: A `BeanFinder` instance, or None if one should be
                automatically created.
            player: If `bean_finder` is None, this is used to construct a
                `BeanFinder` object with the intended player. If `bean_finder`
                is given, this argument should be None (default).
        """
        if bean_finder is None:
            assert player in (None, 0, 1)
            if player is None:
                player = 1
            bean_finder = BeanFinder((38, 13), player)
        else:
            assert player is None
        self.bean_finder = bean_finder

        self.old_board = None  # Board from the previous frame
        self.next_beans = None  # Beans next to fall
        self.current_beans = None  # Beans currently falling
        self.beans_falling = False

    def get_state(self, img, dt=None):
        """Return a PlayerState object representing the current player state.

        Args:
            img: Current video frame of the game.
            dt: The time, in seconds, since the last image given to
                `set_state`. The first time `get_state` is called, this will be
                ignored. If it is left as None, the time will default to the
                time since the last call from `get_state`.

        Returns: PlayerState object representing the state of the player's half
            of the game

        """
        board = self.bean_finder.get_board(img)

        if self.next_beans is None:
            self.next_beans = board.next_beans

        board, new_move = self._is_new_move(self.old_board, board)

        if new_move:
            self.current_beans = self.next_beans
            self.next_beans = board.next_beans
            self.beans_falling = True

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
                if (old_board.board[2][11] == b' ' and
                    new_board.board[2][11] == self.next_beans[1]):

                        new_board.board[2][11] = b' '
                        return new_board, True

                elif (old_board.board[2][11] == b' ' and
                    old_board.board[2][10] == b' ' and
                    new_board.board[2][11] == self.next_beans[0] and
                    new_board.board[2][10] == self.next_beans[1]):

                        new_board.board[2][11] = b' '
                        new_board.board[2][10] = b' '
                        return new_board, True

        return new_board, False
