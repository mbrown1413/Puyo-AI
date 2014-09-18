
from copy import deepcopy

import numpy

# Pixel dimensions of each cell when drawing
CELL_WIDTH = 32
CELL_HEIGHT = 32

VALID_CELLS = (
    b' ',  # Nothing
    b'r',  # Red
    b'g',  # Green
    b'b',  # Blue
    b'y',  # Yellow
    b'p',  # Purple
    b'k',  # Black
)

CELL_COLORS = {
    b' ': (255, 255, 255),
    b'r': (0, 0, 255),
    b'g': (0, 255, 0),
    b'b': (255, 0, 0),
    b'y': (0, 255, 255),
    b'p': (128, 0, 128),
    b'k': (0, 0, 0),
}

def _validate_board(board, width, height):
    if len(board) != width:
        raise ValueError("Initial board given has wrong dimensions: {}".format(board))
    for col in board:
        if len(col) != height:
            raise ValueError("Initial board given has wrong dimensions: {}".format(board))
        for cell in col:
            if cell not in VALID_CELLS:
                raise ValueError('Invalid cell value "{}"'.format(cell))


class Puyo1Board(object):

    def __init__(self, board=None, width=6, height=12):
        self.width = width
        self.height = height
        if board is None:
            self._board = [[b' ' for y in range(height)]
                                 for x in range(width)]
        else:
            _validate_board(board, width, height)
            self._board = deepcopy(board)

    def copy(self):
        return Puyo1Board(self._board, self.width, self.height)

    def draw(self):
        """Return an image representing the puyo board."""

        w = self.width * CELL_WIDTH
        h = self.height * CELL_HEIGHT
        img = numpy.zeros((h, w, 3), "uint8")
        img[:,:,:] = 255

        for x in range(self.width):
            for y in range(self.height):
                cell = self._board[x][y]
                if cell != b' ':
                    x_start = CELL_WIDTH*x
                    y_start = CELL_HEIGHT*y
                    x_end = CELL_WIDTH*(x+1)
                    y_end = CELL_HEIGHT*(y+1)
                    img[y_start:y_end, x_start:x_end] = CELL_COLORS[cell]
        return img

    def drop_beans(self, xs, colors):
        """Drops one or more beans from the top of the board simultaneously.

        TODO: Calculate score and return a namedtuple.

        """
        for x, color in zip(xs, colors):
            self._drop(x, color)

        while self._eliminate_beans() != 0:
            self._do_gravity()

    def drop_black_bean(self, x):
        """Drop a single black bean from the top."""
        self._drop(x, b'k')

    def _drop(self, x, color):
        if color not in VALID_CELLS:
            raise ValueError('Invalid color "{}"'.format(color))
        if x < 0 or x > self.width:
            raise ValueError('Cannot drop bean in out of range x coordinate '
                             '"{}".'.format(x))
        if self._board[x][0] != b' ':
            return  # This column is filled

        for y in range(1, self.height):
            if self._board[x][y] != b' ':
                y = y - 1
                break
        self._board[x][y] = color

    def _eliminate_beans(self):
        n_eliminated = 0

        def eliminate_if_black_bean(x, y):
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return 0
            if self._board[x][y] == b'k':
                self._board[x][y] = b' '
                return 1
            return 0

        for x in range(self.width):
            for y in range(self.height):
                coordinates = self._get_connected(x, y)
                if len(coordinates) < 4:
                    continue

                for x, y in coordinates:
                    n_eliminated += eliminate_if_black_bean(x-1, y)
                    n_eliminated += eliminate_if_black_bean(x+1, y)
                    n_eliminated += eliminate_if_black_bean(x, y-1)
                    n_eliminated += eliminate_if_black_bean(x, y+1)
                    self._board[x][y] = b' '
                    n_eliminated += 1

        return n_eliminated

    def _get_connected(self, x, y):
        """Return a list of coordinates connected by color to (x, y)."""
        color = self._board[x][y]
        if color == b' ' or color == b'k':
            return []

        visited = set()

        def visit(x, y):
            if (x, y) in visited:
                return
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return
            if self._board[x][y] == color:
                visited.add((x, y))

                visit(x-1, y)
                visit(x+1, y)
                visit(x, y-1)
                visit(x, y+1)

        visit(x, y)
        return list(visited)

    def _do_gravity(self):
        """Make floating beans fall."""

        for x in range(self.width):
            for old_y in reversed(range(self.height)):  # Start from bottom up

                new_y = None
                for y in range(old_y+1, self.height):
                    if self._board[x][y] == b' ':
                        new_y = y

                if new_y is not None:
                    self._board[x][new_y] = self._board[x][old_y]
                    self._board[x][old_y] = b' '
