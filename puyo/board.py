
import itertools
from copy import deepcopy
from collections import namedtuple

import numpy

CELL_DRAW_SIZE = (32, 32)

VALID_CELLS = (
    b' ',  # Nothing
    b'r',  # Red
    b'g',  # Green
    b'b',  # Blue
    b'y',  # Yellow
    b'p',  # Purple
    b'k',  # Black
)

# Colors that are drawn for each bean in the `draw()` method
CELL_COLORS = {
    b' ': (255, 255, 255),
    b'r': (0, 0, 255),
    b'g': (0, 255, 0),
    b'b': (255, 0, 0),
    b'y': (0, 255, 255),
    b'p': (128, 0, 128),
    b'k': (0, 0, 0),
}

# Score calculation tables
CHAIN_POWER_TABLE = (0, 8, 16, 32, 64, 128, 256, 512, 999)
COLOR_BONUS_TABLE = (0, 0, 3, 6, 12, 24)
GROUP_BONUS_TABLE = (0, 0, 0, 0, 0, 2, 3, 4, 5, 6, 7, 10)

Combo = namedtuple("Combo", "score n_beans length")

def _validate_board(board, width, height):
    if len(board) != width:
        raise ValueError("Initial board given has wrong dimensions: "
                         "{}".format(board))
    for col in board:
        if len(col) != height:
            raise ValueError("Initial board given has wrong dimensions: "
                             "{}".format(board))
        for cell in col:
            if cell not in VALID_CELLS:
                raise ValueError('Invalid cell value "{}"'.format(cell))


class Puyo1Board(object):
    """One player's board of the Puyo game.

    The board is represented by a 2 dimensional array of beans, 6 wide and 12
    tall, stored in the `board` attribute. The origin is bottom left. Access it
    like this:

        puyo_board = Puyo1Board()
        puyo_board.board[x][y]

    Each cell is one of the following ASCII characters:

        b' ': Nothing
        b'r': Red
        b'g': Green
        b'b': Blue
        b'y': Yellow
        b'p': Purple
        b'k': Black (nuisance)

    The usual way for manipulating the board is through the method
    `make_move()`. There are also some lower level methods which allow for
    moves which could be invalid in an actual game. A typical AI would create a
    list of moves using `iter_moves()`, and return the move it thinks is best.

    The next beans are also stored, in the attribute `next_beans`. If given,
    it's also shown is the image representation returned by `draw()`.

    """

    def __init__(self, board=None, next_beans=None):
        """
        If `board` is given, it should be an length 6 array where each item is
        a 12 length array. Create one like this:

            board = [[blah for y in range(12)]
                           for x in range(6)]

        The given board will be copied upon initialization, so don't worry
        about mutability.

        If `next_beans` is given, it should be a list of 2 bean colors (black,
        or nuisance beans aren't allowed).

        """
        if board is None:
            #TODO: This should really be a numpy array
            self.board = [[b' ' for y in range(12)]
                                 for x in range(6)]
        else:
            _validate_board(board, 6, 12)
            self.board = deepcopy(board)

        if next_beans is not None:
            assert len(next_beans) == 2
            for bean in next_beans:
                assert bean in (b'r', b'g', b'b', b'y', b'p')
        self.next_beans = next_beans
        self.game_over = False

    def copy(self):
        return Puyo1Board(self.board, self.next_beans)

    def draw(self):
        """Return an image representing the puyo board."""

        if self.next_beans:
            w = 8 * CELL_DRAW_SIZE[0]
        else:
            w = 6 * CELL_DRAW_SIZE[0]
        h = 12 * CELL_DRAW_SIZE[1]
        img = numpy.zeros((h, w, 3), "uint8")
        img[:,:,:] = 255

        def draw_square(x, y, color):
            x_start = CELL_DRAW_SIZE[0] * x
            y_start = CELL_DRAW_SIZE[1] * (11 - y)
            x_end = CELL_DRAW_SIZE[0] * (x + 1)
            y_end = CELL_DRAW_SIZE[1] * (12 - y)
            img[y_start:y_end, x_start:x_end] = color

        for x in range(6):
            for y in range(12):
                cell = self.board[x][y]
                if cell != b' ':
                    draw_square(x, y, CELL_COLORS[cell])

        if self.next_beans:
            x_start = CELL_DRAW_SIZE[0] * 6
            y_start = 0
            x_end = CELL_DRAW_SIZE[0] * 8
            y_end = CELL_DRAW_SIZE[1] * 12
            img[y_start:y_end, x_start:x_end] = (127, 127, 127)

            draw_square(7, 9, CELL_COLORS[self.next_beans[0]])
            draw_square(7, 8, CELL_COLORS[self.next_beans[1]])

        return img

    def drop_beans(self, xs, colors):
        """Drops one or more beans from the top of the board simultaneously.

        This method handles gravity, bean elimination and combos. If you're
        actually playing a game, you should use `make_move()`, which is a bit
        higher level since it only allows actually valid moves.

        A Combo object is returned.

        """
        for x, color in zip(xs, colors):
            self._drop(x, color)

        total_score = 0
        total_n_beans = 0
        for i in itertools.count():
            n_beans, n_colors, group_bonus = self._eliminate_beans()
            if n_beans == 0:
                break

            # Calculate Score
            # Based on: http://puyonexus.net/wiki/Scoring
            if i >= len(CHAIN_POWER_TABLE):
                chain_power = CHAIN_POWER_TABLE[-1]
            else:
                chain_power = CHAIN_POWER_TABLE[i]
            color_bonus = COLOR_BONUS_TABLE[n_colors]
            multiplier = chain_power + color_bonus + group_bonus
            multiplier = max(1, min(999, multiplier))
            score = 10 * n_beans * multiplier

            total_score += score
            total_n_beans += n_beans

            self._do_gravity()

        return Combo(total_score, total_n_beans, i)

    def drop_black_bean(self, x):
        """Drop a single black bean from the top."""
        self._drop(x, b'k')

    def make_move(self, beans, orientation, position):
        """Drop a pair of beans as a part of a move in the game.

        This is the method that should be used when actually playing the game,
        as it offers the highest level of abstraction and disallows anything
        illegal in a real game.

        `beans` is a tuple of 2 bean colors. The first item is the top bean,
        the second is the bottom. `orientation` is an integer 0-3 inclusive,
        indicating how many times the pair of beans has been rotated 90 degrees
        clockwise. `position` is an x position on the board, with 0 the
        leftmost position the pair can occupy. If `orientation` is 0 or 2,
        `position` must be between 0-5 inclusive, otherwise it must be between
        0-4 inclusive.

        If an invalid move is given, False is returned. Note that no moves are
        valid if there is a game over. To check if a move is valid beforehand,
        use `can_make_move()`.

        If the given move is valid, the board state is changed and a Combo
        object is returned, which contains information such as the combo's
        score. Note that a Combo object is still returned if zero beans were
        eliminated.

        """
        assert len(beans) == 2
        for bean in beans:
            assert bean in (b'r', b'g', b'b', b'y', b'p')

        if not self.can_make_move(orientation, position):
            return False

        if position == 2 and orientation == 0 and self.board[2][11] != b' ':
            # This column is filled, so it's the only valid move, and results
            # in a game over.
            self.game_over = True
            return Combo(0, 0, 0)

        if orientation > 1:
            orientation -= 2
        else:
            beans = (beans[1], beans[0])

        if orientation == 0:
            return self.drop_beans((position, position), beans)
        else:
            return self.drop_beans((position, position+1), beans)

    def can_make_move(self, orientation, position):
        """Return True if the move can be made, False otherwise."""
        if self.game_over:
            return False

        # Is this even a valid move?
        assert orientation in range(4)
        if orientation % 2 == 0:
            assert position in range(6)
        else:
            assert position in range(5)

        # Any beans blocking the path?
        if position == 2 and orientation == 0:
            # This move is always possible. If this column is completely
            # filled, this move results in a game over.
            return True
        elif position >= 2:
            pos_range = range(2, position+1 + orientation%2)
        else:
            pos_range = range(2, position-1, -1)
        for i in pos_range:
            if self.board[i][11] != b' ':
                return False

        # Make sure there is room to rotate the beans
        #TODO

        return True

    def iter_moves(self):
        """
        Return an iterable of possible moves, as a list of (orientation,
        position) tuples.
        """
        for orientation in range(4):
            for position in range(5 if orientation%2 else 6):
                if self.can_make_move(orientation, position):
                    yield orientation, position

    def is_game_over(self):
        """Has the game been lost?

        The game is lost when the third column is filled and the player is
        forced to drop the next pair of beans above the board. This happens in
        `make_move()`.

        """
        return self.game_over

    def _drop(self, x, color):
        if color not in VALID_CELLS:
            raise ValueError('Invalid color "{}"'.format(color))
        if x < 0 or x > 5:
            raise ValueError('Cannot drop bean at out of range x coordinate '
                             '"{}".'.format(x))

        for y in range(12):
            if self.board[x][y] == b' ':
                self.board[x][y] = color
                break

    def _eliminate_beans(self):

        def eliminate_if_black_bean(x, y):
            if x < 0 or x > 5 or y < 0 or y > 11:
                return 0
            if self.board[x][y] == b'k':
                self.board[x][y] = b' '
                return 1
            return 0

        n_beans = 0
        colors_eliminated = set()
        group_bonus = 0
        for x in range(6):
            for y in range(12):
                coordinates = self.get_connected(x, y)
                if len(coordinates) < 4:
                    continue

                colors_eliminated.add(self.board[x][y])
                if len(coordinates) >= len(GROUP_BONUS_TABLE):
                    group_bonus += GROUP_BONUS_TABLE[-1]
                else:
                    group_bonus += GROUP_BONUS_TABLE[len(coordinates)]

                for x, y in coordinates:
                    n_beans += eliminate_if_black_bean(x-1, y)
                    n_beans += eliminate_if_black_bean(x+1, y)
                    n_beans += eliminate_if_black_bean(x, y-1)
                    n_beans += eliminate_if_black_bean(x, y+1)
                    self.board[x][y] = b' '
                    n_beans += 1

        return n_beans, len(colors_eliminated), group_bonus

    def get_connected(self, x, y):
        """Return a list of coordinates connected by color to (x, y)."""
        color = self.board[x][y]
        if color == b' ' or color == b'k':
            return []

        visited = set()

        def visit(x, y):
            if (x, y) in visited:
                return
            if x < 0 or x >= 6 or y < 0 or y >= 12:
                return
            if self.board[x][y] == color:
                visited.add((x, y))

                visit(x-1, y)
                visit(x+1, y)
                visit(x, y-1)
                visit(x, y+1)

        visit(x, y)
        return list(visited)

    def _do_gravity(self):
        """Make floating beans fall."""

        for x in range(6):
            lowest_free_y = 0
            for y in range(12):

                if self.board[x][y] != b' ':

                    tmp = self.board[x][lowest_free_y]
                    self.board[x][lowest_free_y] = self.board[x][y]
                    self.board[x][y] = tmp

                    lowest_free_y += 1
