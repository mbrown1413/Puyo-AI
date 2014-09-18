
import cv2

from puyo import BeanFinder

def main():

    video = cv2.VideoCapture("footage2/1205.png")
    bean_finder = BeanFinder((38, 13))

    cv2.namedWindow("Frame")
    cv2.namedWindow("Grid")

    i = 0
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
        elif key == ord(" "):
            cv2.imwrite("/tmp/puyo_screenshot_{}.png".format(i), transformed)
            i += 1


if __name__ == "__main__":
    main()
