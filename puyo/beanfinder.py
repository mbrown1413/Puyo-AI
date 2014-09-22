
import os
from math import sqrt
from collections import defaultdict

import cv2

from puyo import Puyo1Board

PLAYER1_BOARD_OFFSET = (35, 35)
CELL_SIZE = (32, 32)
CELL_BORDER = 4

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates/")
BLACK_EYE_TEMPLATE_FILENAME = os.path.join(TEMPLATE_DIR, "black_eye.png")


class BeanFinder(object):

    def __init__(self, screen_offset, player=1):
        if player == 1:
            self.offset = (
                screen_offset[0] + PLAYER1_BOARD_OFFSET[0],
                screen_offset[1] + PLAYER1_BOARD_OFFSET[1],
            )
        elif player == 2:
            raise NotImplementedError()
        else:
            raise ValueError('Invalid player: "{}", '
                              'must be either 1 or 2.'.format(player))

        self.black_eye_template = cv2.imread(BLACK_EYE_TEMPLATE_FILENAME)

    def get_board(self, img):
        board = [[self._get_bean_at(img, x, y) for y in range(12)]
                                               for x in range(6)]
        return Puyo1Board(board)

    def _get_bean_at(self, img, x, y):
        img = self._crop_cell(img, x, y)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        votes = get_color_votes_fast(hsv)

        # It should be rare, but possible to get no similar colors
        if not votes:
            return b' '

        bean = max(votes.items(), key=lambda x: x[1])[0]

        if bean == b' ':
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
            return bean

    def _crop_cell(self, img, x, y):
        x_start = self.offset[0] + CELL_SIZE[0]*x + CELL_BORDER
        y_start = self.offset[1] + CELL_SIZE[1]*y + CELL_BORDER
        x_end = self.offset[0] + CELL_SIZE[0]*(x+1) - CELL_BORDER
        y_end = self.offset[1] + CELL_SIZE[1]*(y+1) - CELL_BORDER
        return img[y_start:y_end, x_start:x_end]

def color_dist(c1, c2):
    return sqrt(
        (c1[0]-c2[0])**2 +
        (c1[1]-c2[1])**2 +
        (c1[2]-c2[2])**2
    )

def get_color_votes(hsv_img):
    BEAN_COLORS = (  # Color values in hsv (0-180, 0-255, 0-255)
        (b' ', (120, 88, 40)),
        (b'r', (165, 154, 200)),
        (b'g', (60, 242, 100)),
        (b'b', (105, 198, 140)),
        (b'y', (15, 110, 140)),
        (b'p', (135, 220, 120)),
    )
    votes = defaultdict(lambda: 0)
    flat_img = hsv_img.reshape(hsv_img.shape[0]*hsv_img.shape[1], 3)
    for pixel in flat_img:
        closest_color = None
        closest_dist = float('inf')
        for color_name, color_value in BEAN_COLORS:
            dist = color_dist(pixel, color_value)
            if dist < closest_dist:
                closest_dist = dist
                closest_color = color_name
        if closest_dist < 50:
            votes[closest_color] += 1

    return votes

import ctypes
LIBRARY_FILE = os.path.join(os.path.dirname(__file__), "libpuyo.so")
print LIBRARY_FILE
libpuyo = ctypes.cdll.LoadLibrary(LIBRARY_FILE)
libpuyo.get_color_votes.argtypes = [ctypes.POINTER(ctypes.c_char), # pixels
                                    ctypes.c_int,                  # n_pixels
                                    ctypes.POINTER(ctypes.c_int),  # strides
                                    ctypes.POINTER(ctypes.c_int)]  # votes_out

def get_color_votes_fast(hsv_img):
    assert hsv_img.dtype == "uint8"
    flat = hsv_img.reshape(hsv_img.shape[0]*hsv_img.shape[1], 3)

    votes_type = ctypes.c_int * 6
    votes = votes_type()
    libpuyo.get_color_votes(
        flat.ctypes.data_as(ctypes.POINTER(ctypes.c_char)),
        flat.shape[0],
        flat.ctypes.strides_as(ctypes.c_int),
        votes
    )

    color_names = (b' ', b'r', b'g', b'b', b'y', b'p')
    return {color_names[i]: votes[i] for i in range(6)}
