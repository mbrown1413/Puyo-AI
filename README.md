
This program plays Puyo Puyo 1. It takes input from a video capture card,
processes the images and outputs controller movements to an Arduino that acts
as a Gamecube controller.

Why only Puyo 1 played on a Gamecube? I own a copy of Dr. Robotnik's Mean Bean
Machine, which is based on Puyo 1, as a part of the Sonic Mega Collection on
the Gamecube. The image recognition and controller output is based on that game
and system, since that's what I have. Everything should be easily adaptable to
other games though.


Status
======

This is a work in progress, but it does run end-to-end. Here's the progress of
each major component:

 * Vision Processing - Determines game state from video input.
   * Status: Complete except for some minor color recognition bugs.
 * Artificial Intelligence - Decides where pieces should be placed based on the
        current game state.
   * Status: There are some simple AIs written, but there is a lot more work to
             do before they are competitive.
 * Game Control - Sends button presses to the game based on the output of the
        AI.
   * Status: Basic functionality finished.

Milestones:

 1. ~~Simple AI controlling the game~~
 1. AI that can beat the early opponents
 1. AI that can beat me (I'm not that good)
 1. AI that can beat the final boss, Dr. Robotnik


Setup
=====

First of all, you'll need:

 * `python2.7`
 * `pyserial`
 * `numpy`
 * `OpenCV` with the `cv2` Python bindings

**TODO**

 * Arduino Setup: **TODO**
 * Video Setup: **TODO**


Usage
=====

`run.py` is the main script that runs all components in tandem. There are also
a bunch of scripts to manually test components. For some of these you can use
`--help` to get details on usage.

 * `run.py` - Plays the game. Recognizes game state through video, decides
        what move to make, and makes it.
 * `gc_send.py` - Sends a command to the arduino controlling the Gamecube.
 * `simulate_ai.py` - For testing AIs. Reproduces the mechanics of the game and
        lets the AI make moves.
 * `simulate_board.py` - For testing the game mechanics. Allows the user to
        test the board mechanics by placing one piece at a time.
 * `recognize_board.py` - For testing the vision processing. Takes video input
        and shows the reconstructed game state.
