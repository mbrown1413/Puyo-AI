#!/usr/bin/python
"""
Sends a command to the Arduino controlling the Gamecube.
"""

from puyo import GamecubeControl

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arduino_serial_device", help='Serial device for the '
        'arduino gamecube controller. Example: "/dev/ttyACM0".')
    parser.add_argument("position", type=int, help="Slot to move the piece "
        "to. The slots are numbered 0 to 5 from left to right. If the piece "
        "is rotated horizontally, slot 5 will be the same as slot 4.")
    parser.add_argument("rotation", type=int, help="Number of times to rotate "
        "the piece clockwise.")
    args = parser.parse_args()

    controller = GamecubeControl(args.arduino_serial_device)
    controller.puyo_move(args.position, args.rotation)

if __name__ == "__main__":
    main()
