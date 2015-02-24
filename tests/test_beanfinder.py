#!/usr/bin/python

import os
import unittest

import cv2

import puyo

from helper import board_from_strs, PuyoTestCase


TEST_IMG_FOLDER = os.path.join(os.path.dirname(__file__), "img")


class TestBeanFinder(PuyoTestCase):

    def assertImageMatchesBoard(self, img_filename, board):
        bean_finder = puyo.BeanFinder((38, 13), 1)
        img = cv2.imread(os.path.join(TEST_IMG_FOLDER, img_filename))
        if img is None:
            raise OSError("Image not found")
        recognized_board = bean_finder.get_board(img)
        self.assertBoardEquals(board, recognized_board)

    def assertImageHasSpecialState(self, img_filename, actual_state):
        bean_finder = puyo.BeanFinder((38, 13), 1)
        img = cv2.imread(os.path.join(TEST_IMG_FOLDER, img_filename))
        if img is None:
            raise OSError("Image not found")
        recognized_state = bean_finder.get_special_game_state(img)
        self.assertEqual(recognized_state, actual_state)

    def test_recognition_1(self):
        """Simple image with no nussance beans."""
        board = board_from_strs([
            b"r     ",
            b"r     ",
            b"g     ",
            b"p g g ",
            b"r p y ",
            b"yprrb ",
            b"ppypyr",
            b"yygbbr",
            b"rbpryp",
        ], next_beans=(b'p', b'y'))
        self.assertImageMatchesBoard("beanfinder_1.png", board)

    def test_recognition_2(self):
        """
        More complex image with nussance beans and sweat from the monkey
        obscuring some beans.
        """
        board = board_from_strs([
            b"bb    ",
            b"rp    ",
            b"rr    ",
            b"pp  b ",
            b"rp  y ",
            b"pb  k ",
            b"kkr gk",
            b"rgbbyy",
            b"rgbryk",
            b"rprrgg",
            b"bbbyyp",
            b"rgpypg",
        ], next_beans=(b'b', b'p'))
        self.assertImageMatchesBoard("beanfinder_2.png", board)

    def test_yellow_similar_to_green(self):
        """
        This is a test image where x=2 y=5 sometimes gets counted as green,
        instead of yellow.
        """
        board = board_from_strs([
            b"  y   ",
            b"  y   ",
            b"  y   ",
            b"y g   ",
            b"g ggp ",
            b"r ypr ",
            b"rryyrg",
            b"gypryg",
        ], next_beans=(b'y', b'p'))
        self.assertImageMatchesBoard("beanfinder_yellow_similar_to_green.png", board)

    def test_board_state_unknown(self):
        self.assertImageHasSpecialState("beanfinder_1.png", "unknown")
        self.assertImageHasSpecialState("beanfinder_2.png", "unknown")
        self.assertImageHasSpecialState("beanfinder_yellow_similar_to_green.png", "unknown")

    def test_board_state_won(self):
        self.assertImageHasSpecialState("beanfinder_scenario_won.png", "scenario_won")

    def test_board_state_lost(self):
        self.assertImageHasSpecialState("beanfinder_scenario_lost.png", "scenario_lost")

    def test_board_state_continue(self):
        self.assertImageHasSpecialState("beanfinder_scenario_continue.png", "scenario_continue")


if __name__ == "__main__":
    unittest.main()
