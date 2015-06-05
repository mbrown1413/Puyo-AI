#!/usr/bin/python
"""
Play Puyo Puyo by taking video input and sending commands to an Arduino based
Gamecube controller.
"""

from time import sleep

import cv2

import puyo


PASSWORD_TOKEN_ORDER = (
    'r', 'y', 'b', 'p', 'g', 'n',  # Beans
    'c',  # Carbuncle (little dancing dude)
    'left', 'right', 'end'  # Controls
)
PASSWORDS = {
    7:  "pbgc",
    8:  "gcny",
    9:  "bpcc",
    10: "cryn",
    11: "nrrb",
    12: "ggny",
}
def enter_password(controller, level):
    password = PASSWORDS[level]

    cur_idx = 0
    for token in tuple(password)+("end",):
        token_idx = PASSWORD_TOKEN_ORDER.index(token)
        direction = "left" if cur_idx > token_idx else "right"
        for i in range(abs(cur_idx - token_idx)):
            controller.push_button(direction)
            sleep(0.2)
        controller.push_button("b")
        sleep(0.1)
        cur_idx = token_idx

def get_to_password_screen(controller):
    for button in ("z", "up", "a", "up", "a"):
        controller.push_button(button)
        sleep(0.05)

    sleep(4.5); controller.push_button("start")
    sleep(2);   controller.push_button("start")
    sleep(2);   controller.push_button("start")
    sleep(2);   controller.push_button("a")
    sleep(1.0); controller.push_button("down")
    sleep(0.1); controller.push_button("a")
    sleep(1.5);


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
             "available for the following levels: {}".format(PASSWORDS.keys()))
    parser.add_argument("--debug", "-d", default=False, action="store_true",
        help="Show debug window and other debug information.")
    args = parser.parse_args()

    #TODO: Make screen offset configurable
    controller = puyo.GamecubeController(args.gc_dev)
    driver = puyo.Driver(controller, args.ai, args.player)

    if args.level:
        if args.level not in PASSWORDS:
            parser.error('Password not available for level "{}"'.format(args.level))
        get_to_password_screen(controller)
        enter_password(controller, args.level)

    driver.run(args.video, video_out=args.video_out, debug=args.debug)


if __name__ == "__main__":
    main()
