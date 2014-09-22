
import cv2

from puyo import BeanFinder

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
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Video source filename or camera index")
    parser.add_argument("--player1", "-1", dest="player", const=1,
        action="store_const", help="Play as player 1. Reads the left side of "
        "the screen. (default)", default=1)
    parser.add_argument("--player2", "-2", dest="player", const=2,
        action="store_const", help="Play as player 2. Reads the right side "
        "of the screen.")
    args = parser.parse_args()

    video = open_video(args.source)
    if not video:
        print("Cannot open video stream")
        import sys
        sys.exit(1)

    bean_finder = BeanFinder((38, 13), args.player)
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

        board = bean_finder.get_board(img)
        cv2.imshow("Grid", board.draw())

        key = cv2.waitKey(10) % 256
        if key == 27:  # Escape
            break


if __name__ == "__main__":
    main()
