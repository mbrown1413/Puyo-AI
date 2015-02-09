
import sys
import os.path

import cv2

from puyo import BeanFinder


def main():
    in_filename = sys.argv[1]
    out_folder = sys.argv[2]
    prefix = os.path.basename(in_filename)[:-4]

    bean_finder = BeanFinder((38, 13))
    in_img = cv2.imread(in_filename)
    if in_img is None:
        raise OSError("Couldn't open input image")

    for x in range(6):
        for y in range(12):
            cell_img = bean_finder._crop_cell(in_img, x, y)

            out_filename = "{}_{}_{}.png".format(prefix, x, y)
            out_path = os.path.join(out_folder, out_filename)
            cv2.imwrite(out_path, cell_img)

if __name__ == "__main__":
    main()
