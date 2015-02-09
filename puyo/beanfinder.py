
from __future__ import division
import os
from math import sqrt
from collections import defaultdict

import cv2
import numpy

from puyo import Board

CELL_CROP_SIZE = (32, 32)
CELL_BORDER = 4

PLAYER1_BOARD_OFFSET = (35, 35)
PLAYER2_BOARD_OFFSET = (419, 35)
PLAYER1_NEXT_BEAN_OFFSETS = ((258, 96), (258, 127))
PLAYER2_NEXT_BEAN_OFFSETS = ((354, 96), (354, 127))

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates/")
BLACK_EYE_TEMPLATE_FILENAME = os.path.join(TEMPLATE_DIR, "black_eye.png")

# Average hue histograms for each color, used to match colors.
# See `vision_training/` for steps to reproduce this data.
HUE_HISTOGRAMS = {
    b' ': numpy.array([0.02119149952244509, 0.68812679083094497,
        4.5709467526265533, 3.6332975167144221, 2.1353420487106014,
        1.7077811604584523, 2.0388610315186249, 0.20415472779369639,
        0.00014923591212989497, 0.00014923591212989497, 0.0, 0.0, 0.0, 0.0,
        0.0]),
    b'b': numpy.array([0.0022163120567375888, 0.0099734042553191477,
        0.12965425531914893, 1.0261524822695034, 0.97185283687943269,
        5.4222074468085086, 7.4324024822695041, 0.0055407801418439736, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    b'g': numpy.array([0.0021258503401360546, 0.06164965986394557,
        1.6937712585034013, 12.008928571428571, 0.74564200680272119,
        0.23384353741496597, 0.22108843537414968, 0.032950680272108852, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    b'p': numpy.array([0.066287878787878785, 0.1259469696969697,
        0.30160984848484845, 0.32054924242424238, 0.14962121212121215,
        0.11931818181818174, 0.18655303030303036, 3.2831439393939399,
        10.360795454545457, 0.07670454545454547, 0.0094696969696969717, 0.0,
        0.0, 0.0, 0.0]),
    b'r': numpy.array([5.2842514124293771, 0.32750706214689262,
        0.4087217514124295, 0.25688559322033905, 0.14256709039548027,
        0.090925141242937824, 0.08121468926553671, 0.079449152542372892,
        0.058262711864406777, 0.6320621468926555, 7.6381532485875701, 0.0, 0.0,
        0.0, 0.0]),
    b'y': numpy.array([3.2574728260869557, 10.179272342995169,
        0.77898550724637683, 0.18493357487922707, 0.11096014492753625,
        0.041515700483091757, 0.063405797101449279, 0.020380434782608696,
        0.0022644927536231889, 0.030193236714975855, 0.33061594202898553, 0.0,
        0.0, 0.0, 0.0]),
}
HIST_N_BINS = len(HUE_HISTOGRAMS[b'r'])

def compare_hist(hist_a, hist_b):
    return numpy.sum((hist_a - hist_b)**2)


class BeanFinder(object):
    """Stateless component of vision recognition.

    Recognizes the placement of beans for a single player, including the next
    pair of beans.

    """

    def __init__(self, screen_offset, player=1):
        if player == 1:
            board_offset = PLAYER1_BOARD_OFFSET
            next_bean_offsets = PLAYER1_NEXT_BEAN_OFFSETS
        elif player == 2:
            board_offset = PLAYER2_BOARD_OFFSET
            next_bean_offsets = PLAYER2_NEXT_BEAN_OFFSETS
        else:
            raise ValueError('Invalid player: "{}", '
                              'must be either 1 or 2.'.format(player))
        self.board_offset = (
            screen_offset[0] + board_offset[0],
            screen_offset[1] + board_offset[1],
        )
        self.next_bean_offsets = (
            (screen_offset[0] + next_bean_offsets[0][0],
                screen_offset[1] + next_bean_offsets[0][1]),
            (screen_offset[0] + next_bean_offsets[1][0],
                screen_offset[1] + next_bean_offsets[1][1])
        )

        self.black_eye_template = cv2.imread(BLACK_EYE_TEMPLATE_FILENAME)

    def get_board(self, img):
        board = [[self._get_bean_at(img, x, y) for y in range(12)]
                                               for x in range(6)]
        next_beans = self._get_next_beans(img)
        return Board(board, next_beans)

    def _get_bean_at(self, img, x, y):
        return self._detect_color(self._crop_cell(img, x, y))

    def _get_next_beans(self, img):
        next1 = self._crop_cell(img,
                                *self.next_bean_offsets[0],
                                image_coordinates=True)
        next2 = self._crop_cell(img,
                                *self.next_bean_offsets[1],
                                image_coordinates=True)
        next_beans = (self._detect_color(next1), self._detect_color(next2))
        if next_beans[0] not in (b'r', b'g', b'b', b'y', b'p') or \
           next_beans[1] not in (b'r', b'g', b'b', b'y', b'p'):
            next_beans = None
        return next_beans

    def _detect_color(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) / 255
        hues = [p[0] for p in hsv.reshape((-1, 3))]
        hist, _ = numpy.histogram(hues, HIST_N_BINS, (0, 1), density=True)

        closest_dist = float('inf')
        closest_color = None
        for color, color_hist in HUE_HISTOGRAMS.iteritems():
            dist = compare_hist(hist, color_hist)
            if dist < closest_dist:
                closest_dist = dist
                closest_color = color

        if closest_color in (b' ', b'k'):
            # Black and background have very similar colors. Use template
            # matching on the black bean's eyes to tell the difference.
            match = cv2.matchTemplate(img,
                                      self.black_eye_template,
                                      cv2.TM_CCOEFF)
            max_value = cv2.minMaxLoc(match)[1]
            if max_value > 500000:
                return b'k'
            else:
                return b' '
        else:
            return closest_color

    def _crop_cell(self, img, x, y, image_coordinates=False):
        """
        By default, (x, y) are treaed as board coordinates (so 0 <= x < 6 and
        y <= y < 12, with (0, 0) being the lower left). If `image_coordinates`
        is True, (x, y) is treated as pixel coordinates starting from the
        upper left of the image.
        """
        if not image_coordinates:
            x = self.board_offset[0] + x * CELL_CROP_SIZE[0]
            y = self.board_offset[1] + (11-y) * CELL_CROP_SIZE[1]
            offset = self.board_offset

        x_start = x + CELL_BORDER
        y_start = y + CELL_BORDER
        x_end   = x - CELL_BORDER + CELL_CROP_SIZE[0]
        y_end   = y - CELL_BORDER + CELL_CROP_SIZE[1]
        return img[y_start:y_end, x_start:x_end]
