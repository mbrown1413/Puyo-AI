#!/usr/bin/python
"""
Play Puyo Puyo by taking video input and sending commands to an Arduino based
Gamecube controller.
"""

import cv2

import puyo

def open_video(source):
    video = cv2.VideoCapture(source)

    if not video.isOpened():
        try:
            integer = int(source)
        except ValueError:
            pass
        else:
            video = cv2.VideoCapture(integer)

    if not video.isOpened():
        return None
    return video

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
    args = parser.parse_args()

    video = open_video(args.video)
    if not video:
        print("Cannot open video stream")
        import sys
        sys.exit(1)

    #TODO: Make screen offset configurable
    vision = puyo.PuyoVision(player=1)
    cv2.namedWindow("Frame")
    cv2.namedWindow("Grid")

    ai = puyo.AI_REGISTRY[args.ai]()
    controller = puyo.GamecubeControl(args.gc_dev)

    current_beans = None
    while True:

        was_read, img = video.read()
        if not was_read:
            print("Error: Could not read video frame!")
            if cv2.waitKey(-1) % 256:
                break
            continue
        cv2.imshow("Frame", img)

        state = vision.get_state(img)
        cv2.imshow("Grid", state.board.draw())

        if state.new_move:
            pos, rot = ai.get_move(state.board.copy(), current_beans)
            controller.puyo_move(pos, rot)

        current_beans = state.board.next_beans

        key = cv2.waitKey(10) % 256
        if key == 27:  # Escape
            break


if __name__ == "__main__":
    main()
