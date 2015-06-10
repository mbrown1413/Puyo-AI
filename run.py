#!/usr/bin/python
"""
Play Puyo Puyo by taking video input and sending commands to an Arduino based
Gamecube controller.
"""

from time import sleep

import cv2

import puyo




def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", help='Video source. An AVI filename, camera '
        'index (ex: "0" to use /dev/video0), or format specifier (ex: '
        '"footage/%%d.jpg"). Any format supported by the installed version of '
        'OpenCV will work.')
    parser.add_argument("gc_dev", help='Serial device for the Arduino '
        'Gamecube controller. Example: "/dev/ttyACM0".')
    ai_names = list(puyo.AI_REGISTRY.keys())
    parser.add_argument("-a", "--ai", choices=ai_names,
        default=puyo.DEFAULT_AI_NAME, help="AI to use. Choose one of: {} "
        "(default: {})".format(ai_names, puyo.DEFAULT_AI_NAME))
    parser.add_argument("--player2", "-2", dest="player", const=2,
        action="store_const", help="Play as player 2. Plays on the right side "
        "of the screen.")
    parser.add_argument("--video-out", "-o", default=None,
        help="AVI file to write video to.")
    parser.add_argument("--level", "-l", default=None, type=int,
        help="Reset the game and start on the given level by entering a "
             "passcode. Default: start playing immediately. Passcodes are "
             "available for the following levels: {}".format(puyo.PASSWORDS.keys()))
    parser.add_argument("--mode", "-m", default="scenario",
        choices=("scenario", "repeat"),
        help="scenario (default): Assume the game is already started in "
            "scenario and progress accordingly. repeat: Repeatedly do one "
            "scenario level, specified by --level (-l).")
    parser.add_argument("--debug", "-d", default=False, action="store_true",
        help="Show debug window and other debug information.")
    args = parser.parse_args()

    #TODO: Make screen offset configurable
    controller = puyo.GamecubeController(args.gc_dev)
    driver = puyo.Driver(controller, args.ai, args.player)

    if args.level is not None:
        driver.reset_to_level(args.level)

    if args.mode == "scenario":
        driver.run(args.video, video_out=args.video_out, debug=args.debug)
    elif args.mode == "repeat":
        if not args.level:
            parser.error("level argument must be given when mode is repeat")

        won = 0
        total = 0
        while True:
            state = driver.run(args.video, video_out=args.video_out, on_special_state="exit", debug=args.debug)
            if state.special_state == "unknown":
                break  # Must have exited manually from debug mode

            if state.special_state == "scenario_won":
                won += 1
            total += 1
            print
            print "AI: {}".format(args.ai)
            print "Level: {}".format(args.level)
            print "Match Result: {} ({} / {})".format(state.special_state, won, total)

            driver.reset_to_level(args.level)

if __name__ == "__main__":
    main()
