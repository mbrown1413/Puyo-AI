
from copy import deepcopy

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

    def __init__(self, board=None, next_beans=None):
        if board is None:
            self.board = [[b' ' for y in range(12)]
                                 for x in range(6)]
        else:
            _validate_board(board, 6, 12)
            self.board = deepcopy(board)

        self.next_beans = next_beans

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
        if x < 0 or x > 5:
            raise ValueError('Cannot drop bean at out of range x coordinate '
                             '"{}".'.format(x))

        for y in range(12):
            if self.board[x][y] == b' ':
                self.board[x][y] = color
                break

    def _eliminate_beans(self):
        n_eliminated = 0

        def eliminate_if_black_bean(x, y):
            if x < 0 or x > 5 or y < 0 or y > 11:
                return 0
            if self.board[x][y] == b'k':
                self.board[x][y] = b' '
                return 1
            return 0

        for x in range(6):
            for y in range(12):
                coordinates = self._get_connected(x, y)
                if len(coordinates) < 4:
                    continue

                for x, y in coordinates:
                    n_eliminated += eliminate_if_black_bean(x-1, y)
                    n_eliminated += eliminate_if_black_bean(x+1, y)
                    n_eliminated += eliminate_if_black_bean(x, y-1)
                    n_eliminated += eliminate_if_black_bean(x, y+1)
                    self.board[x][y] = b' '
                    n_eliminated += 1

        return n_eliminated

    def _get_connected(self, x, y):
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
