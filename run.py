
import sys

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

    video = open_video(sys.argv[1])
    if not video:
        print("Cannot open video stream")
        sys.exit(1)

    #TODO: Make screen offset configurable
    bean_finder = puyo.BeanFinder((38, 13), 1)
    cv2.namedWindow("Frame")
    cv2.namedWindow("Grid")

    ai = puyo.SimpleComboAI()
    controller = puyo.GamecubeControl(sys.argv[2])

    current_beans = None
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

        if current_beans is not None and current_beans != board.next_beans:
            print current_beans
            orientation, position = ai.move(board, current_beans)
            controller.puyo_move(position, orientation)
        current_beans = board.next_beans

        key = cv2.waitKey(10) % 256
        if key == 27:  # Escape
            break


if __name__ == "__main__":
    main()
