#!/usr/bin/python
"""
Sends a command to the Arduino controlling the Gamecube.
"""

from puyo import GamecubeController

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gc_dev", help='Serial device for the Arduino '
        'Gamecube controller. Example: "/dev/ttyACM0".')
    parser.add_argument("position", type=int, help="Slot to move the piece "
        "to. The slots are numbered 0 to 5 from left to right. If the piece "
        "is rotated horizontally, slot 5 will be the same as slot 4.")
    parser.add_argument("rotation", type=int, help="Number of times to rotate "
        "the piece clockwise.")
    args = parser.parse_args()

    controller = GamecubeController(args.gc_dev)
    controller.puyo_move(args.position, args.rotation)

if __name__ == "__main__":
    main()
