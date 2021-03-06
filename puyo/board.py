
import os
import random
import itertools
from collections import namedtuple
import ctypes

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
    b'b': (200, 200, 0),
    b'y': (0, 255, 255),
    b'p': (128, 0, 128),
    b'k': (0, 0, 0),
}

# Score calculation tables
CHAIN_POWER_TABLE = (0, 8, 16, 32, 64, 128, 256, 512, 999)
COLOR_BONUS_TABLE = (0, 0, 3, 6, 12, 24)
GROUP_BONUS_TABLE = (0, 0, 0, 0, 0, 2, 3, 4, 5, 6, 7, 10)

Combo = namedtuple("Combo", "score n_beans length game_over")


libpuyo = None
ctypes_loaded = False
ctypes_load_failed = False
def _load_ctypes():
    global libpuyo, ctypes_loaded, ctypes_load_failed
    if ctypes_loaded:
        return True
    if ctypes_load_failed:
        return False

    LIBRARY_FILE = os.path.join(os.path.dirname(__file__), "libpuyo.so")
    try:
        libpuyo = ctypes.cdll.LoadLibrary(LIBRARY_FILE)
    except OSError as e:
        print e
        print 'Warning: Error loading C library, processing may be slow.'
        print '    Use "make" to compile if "puyo/libpuyo.so" is not present.'
        ctypes_load_failed = True
        return False
    libpuyo.board_eliminate_beans.argtypes = [
        ctypes.POINTER(ctypes.c_char),   # board
        ctypes.POINTER(ctypes.c_int),  # strides
        ctypes.POINTER(ctypes.c_int),  # n_beans_out
        ctypes.POINTER(ctypes.c_int),  # n_colors_eliminated_out
        ctypes.POINTER(ctypes.c_int),  # group_bonus_out
    ]
    ctypes_loaded = True
    return True


def _validate_board(cells):
    assert cells.shape == (6, 12)
    for col in cells:
        for cell in col:
            if cell not in VALID_CELLS:
                raise ValueError('Invalid cell value "{}"'.format(cell))


class Board(object):
    """A single player's board of the Puyo game.

    The board is represented by a 2 dimensional array of beans, 6 wide and 12
    tall, stored in the `board` attribute. The origin is bottom left. Access it
    like this:

        puyo_board = Board()
        puyo_board[x,y]  # Get cell at (x, y)
        puyo_board[x,y] = b'r'  # Set (x, y) to red

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
    moves which could be invalid in an actual game, such as directly accessing
    the cells as described above. A typical AI would create a list of moves
    using `iter_moves()`, and return the move it thinks is best.

    The next beans are also stored, in the attribute `next_beans`. If given,
    it's also shown is the image representation returned by `draw()`.

    """

    def __init__(self, cells=None, next_beans=None, c_accelerated=True):
        """
        If `cells` is given, it should be an length 6 array where each item is
        a 12 length array. Create one like this:

            cells = [[blah for y in range(12)]
                           for x in range(6)]

        where the lower left is `cells[0][0]` and the upper left is
        `cells[0][11]`. The given board will be copied upon initialization, so
        don't worry about mutability.

        If `next_beans` is given, it should be a list of 2 bean colors (black,
        or nuisance beans aren't allowed).

        """
        if cells is None:
            self._cells = numpy.array([[b' ' for y in range(12)]
                                             for x in range(6)], dtype="|S1")
        else:
            self._cells = numpy.array(cells, dtype="|S1")
            _validate_board(self._cells)

        if next_beans is not None:
            assert len(next_beans) == 2
            for bean in next_beans:
                assert bean in (b'r', b'g', b'b', b'y', b'p')
        self.next_beans = next_beans

        self.c_accelerated = c_accelerated
        if self.c_accelerated:
            if not _load_ctypes():
                self.c_accelerated = False

    def __eq__(self, other):
        if isinstance(other, Board):
            return (self._cells == other._cells).all() and \
                    self.next_beans == other.next_beans
        return NotImplemented

    def __getitem__(self, key):
        return self._cells.__getitem__(key)

    def __setitem__(self, key, value):
        assert value in VALID_CELLS
        self._cells.__setitem__(key, value)

    def get_array(self):
        return self._cells[:]

    def copy(self):
        return Board(self._cells, self.next_beans)

    def count(self, color=None):
        """
        Count cells with the given color. If `color` is None, count all beans
        (including nuisance).
        """
        ret = 0
        for x, y in itertools.product(range(6), range(12)):
            value = self._cells[x][y]
            if value == color or (color is None and value != b' '):
                ret += 1
        return ret

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
                cell = self._cells[x][y]
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

            self._do_gravity()

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

        return Combo(total_score, total_n_beans, i, False)

    def drop_bean(self, x, color):
        """Shortcut for `drop_beans([x], [color])`."""
        return self.drop_beans([x], [color])

    def drop_nuisance(self, n=1):
        """Drop 'n' nuisance beans."""

        # Distribute as evenly as possible, randomly dropping the last 1-5 if
        # `n` is not a multiple of 6
        to_drop_in_col = [n // 6 for x in range(6)]
        n -= (n // 6) * 6
        xs = range(6)
        random.shuffle(xs)
        for x in xs[:n]:
            to_drop_in_col[x] += 1

        for x, to_drop in enumerate(to_drop_in_col):
            for i in range(to_drop):
                self._drop(x, b'k')

    def make_move(self, beans, position, rotation):
        """Drop a pair of beans as a part of a move in the game.

        This is the method that should be used when actually playing the game,
        as it offers the highest level of abstraction and disallows anything
        illegal in a real game.

        Args:
            beans: A tuple of 2 bean colors. The first item is the top bean,
                the second is the bottom.
            position: The position to place the pieces, with 0 being the
                leftmost position the pair can occupy. This meaning depends on
                how the pieces will be rotated. If `rotation` is 0 or 2
                (vertical), `position` must be between 0-5 inclusive. If
                `rotation` is 1 or 3 (horizontal) it must be between 0-4
                inclusive.
            rotation: How many times to rotate the pieces clockwise. An
                integer 0-3 inclusive.

        Returns:
            If the given move is valid, the board is mutated and a Combo
            object is returned. If the given move is invalid, False is
            returned. You can check beforehand to see if a move is valid with
            `can_make_move()`.

        """
        assert len(beans) == 2
        for bean in beans:
            assert bean in (b'r', b'g', b'b', b'y', b'p')

        if not self.can_make_move(position, rotation):
            return False

        if position == 2 and rotation == 0 and self._cells[2][11] != b' ':
            # This column is filled, so it's the only valid move, and results
            # in a game over.
            return Combo(0, 0, 0, True)

        if rotation > 1:
            rotation -= 2
        else:
            beans = (beans[1], beans[0])

        if rotation == 0:
            return self.drop_beans((position, position), beans)
        else:
            return self.drop_beans((position, position+1), beans)

    def can_make_move(self, position, rotation):
        """Return True if the move can be made, False otherwise."""

        # Is this even a valid move?
        assert rotation in range(4)
        if rotation % 2 == 0:
            assert position in range(6)
        else:
            assert position in range(5)

        # Any beans blocking the path?
        if position == 2 and rotation == 0:
            # This move is always possible. If this column is completely
            # filled, this move results in a game over.
            return True
        elif position >= 2:
            pos_range = range(2, position+1 + rotation%2)
        else:
            pos_range = range(2, position-1, -1)
        for i in pos_range:
            if self._cells[i][11] != b' ':
                return False

        # Make sure there is room to rotate the beans
        if rotation != 0 and self._cells[1][11] != b' ' and \
                             self._cells[3][11] != b' ':
            return False

        return True

    def iter_moves(self):
        """
        Return an iterable of possible moves, as a list of (position,
        rotation) tuples.
        """
        for rotation in range(4):
            for position in range(5 if rotation%2 else 6):
                if self.can_make_move(position, rotation):
                    yield position, rotation

    def _drop(self, x, color):
        if color not in VALID_CELLS:
            raise ValueError('Invalid color "{}"'.format(color))
        if x < 0 or x > 5:
            raise ValueError('Cannot drop bean at out of range x coordinate '
                             '"{}".'.format(x))

        for y in range(12):
            if self._cells[x][y] == b' ':
                self._cells[x][y] = color
                break

    def _eliminate_beans(self):
        if self.c_accelerated:
            return self._eliminate_beans_c()
        else:
            return self._eliminate_beans_py()

    def _eliminate_beans_c(self):
        n_beans = ctypes.c_int()
        n_colors_eliminated = ctypes.c_int()
        group_bonus = ctypes.c_int()
        libpuyo.board_eliminate_beans(
            self._cells.ctypes.data_as(ctypes.POINTER(ctypes.c_char)),
            self._cells.ctypes.strides_as(ctypes.c_int),
            ctypes.pointer(n_beans),
            ctypes.pointer(n_colors_eliminated),
            ctypes.pointer(group_bonus)
        )
        return n_beans.value, n_colors_eliminated.value, group_bonus.value

    def _eliminate_beans_py(self):

        def eliminate_if_black_bean(x, y):
            if x < 0 or x > 5 or y < 0 or y > 11:
                return
            if self._cells[x][y] == b'k':
                self._cells[x][y] = b' '

        n_beans = 0
        colors_eliminated = set()
        group_bonus = 0
        for x in range(6):
            for y in range(12):
                if self._cells[x][y] == b' ' or self._cells[x][y] == b'k':
                    continue
                coordinates = self.get_connected(x, y)
                if len(coordinates) < 4:
                    continue

                colors_eliminated.add(self._cells[x][y])
                if len(coordinates) >= len(GROUP_BONUS_TABLE):
                    group_bonus += GROUP_BONUS_TABLE[-1]
                else:
                    group_bonus += GROUP_BONUS_TABLE[len(coordinates)]

                for x, y in coordinates:
                    eliminate_if_black_bean(x-1, y)
                    eliminate_if_black_bean(x+1, y)
                    eliminate_if_black_bean(x, y-1)
                    eliminate_if_black_bean(x, y+1)
                    self._cells[x][y] = b' '
                    n_beans += 1

        return n_beans, len(colors_eliminated), group_bonus

    def get_connected(self, x, y):
        """Return a list of coordinates connected by color to (x, y)."""
        color = self._cells[x][y]
        if color == b' ' or color == b'k':
            return []

        visited = set()

        def visit(x, y):
            if (x, y) in visited:
                return
            if x < 0 or x >= 6 or y < 0 or y >= 12:
                return
            if self._cells[x][y] == color:
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

                if self._cells[x][y] != b' ':

                    tmp = self._cells[x][lowest_free_y]
                    self._cells[x][lowest_free_y] = self._cells[x][y]
                    self._cells[x][y] = tmp

                    lowest_free_y += 1
