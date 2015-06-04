#!/usr/bin/python
"""
Play Puyo Puyo by taking video input and sending commands to an Arduino based
Gamecube controller.
"""

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
    parser.add_argument("--debug", "-d", default=False, action="store_true",
        help="Show debug window and other debug information.")
    args = parser.parse_args()

    #TODO: Make screen offset configurable
    controller = puyo.GamecubeController(args.gc_dev)
    driver = puyo.Driver(controller, args.ai, args.player)

    driver.run(args.video, video_out=args.video_out, debug=args.debug)


if __name__ == "__main__":
    main()
