
import sys

import serial

from puyo import GamecubeControl

def main():
    controller = GamecubeControl(sys.argv[1])

    pos = int(sys.argv[2])
    rot = int(sys.argv[3])
    controller.puyo_move(pos, rot)

if __name__ == "__main__":
    main()
