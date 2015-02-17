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
    parser.add_argument("--player2", "-2", dest="player", const=2,
        action="store_const", help="Play as player 2. Plays on the right side "
        "of the screen.")
    parser.add_argument("--video-out", "-o", default=None,
        help="AVI file to write video to.")
    args = parser.parse_args()

    video = open_video(args.video)
    if not video:
        print("Cannot open video stream")
        import sys
        sys.exit(1)

    #TODO: Make screen offset configurable
    controller = puyo.GamecubeController(args.gc_dev)
    driver = puyo.Driver(controller, args.ai, args.player)

    video_writer = None
    cv2.namedWindow("Frame")
    cv2.namedWindow("Grid")
    while True:

        was_read, img = video.read()
        if not was_read:
            print("Error: Could not read video frame!")
            if cv2.waitKey(-1) % 256:
                break
            continue
        cv2.imshow("Frame", img)

        state = driver.step(img)
        cv2.imshow("Grid", state.board.draw())

        if args.video_out:
            if video_writer is None:
                fourcc = cv2.cv.CV_FOURCC(*"I420")
                video_writer = cv2.VideoWriter(args.video_out, fourcc, 25, (img.shape[1], img.shape[0]), True)
            video_writer.write(img)

        key = cv2.waitKey(10) % 256
        if key == 27:  # Escape
            break

    if video_writer is not None:
        video_writer.release()


if __name__ == "__main__":
    main()
