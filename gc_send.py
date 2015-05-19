#!/usr/bin/python
"""
Sends a command to the Arduino controlling the Gamecube.

The command can either be a single button, or a Puyo move spec (a column and a
rotation separated by a comma but no space). Examples:

    `Start`
    `0,3` - Leftmost column, rotate 3 times clockwise
    `5,1` - Rightmost column, rotate 1 time clockwise
    `A`
    `Down` - Joystick all the way down

In the case of a button press, the button is held for a brief amount of time.
In the case of a Puyo move, it is executed as fast as possible.

"""

from puyo import GamecubeController

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("gc_dev", help='Serial device for the Arduino '
        'Gamecube controller. Example: "/dev/ttyACM0" or "/dev/ttyUSB0".')
    parser.add_argument("command", help='Either the name of a '
        'button/movement, or a puyo move specification (a column and a '
        'rotation separated by a comma with no space, eg. "0,3"). Valid '
        'buttons are: {}'.format(GamecubeController.BUTTON_BITS.keys()))
    args = parser.parse_args()

    comma_count = args.command.count(',')

    # Button Press
    if comma_count == 0:
        args.command = args.command.lower()
        if args.command not in GamecubeController.BUTTON_BITS:
            parser.error('Invalid button "{}". Valid buttons are: '
                    '{}'.format(args.command,
                                GamecubeController.BUTTON_BITS.keys()))
        controller = GamecubeController(args.gc_dev)
        controller.push_button(args.command)

    # Puyo Move
    elif comma_count == 1:

        def validate(parser, name, min_x, max_x, x):
            error = False
            try:
                x = int(x)
            except ValueError:
                error = True
            if x < min_x or x > max_x:
                error = True
            if error:
                parser.error('{} must be an integer between {} and {} '
                        'inclusive, not "{}"'.format(name, min_x, max_x, x))
                raise RuntimeError()
            return x

        controller = GamecubeController(args.gc_dev)
        col, rot = args.command.split(',', 1)
        col = validate(parser, "Column", 0, 6, col)
        rot = validate(parser, "Rotation", -3, 3, rot)
        controller.puyo_move(col, rot)

    else:
        parser.error("Error parsing command argument: Too many commas")

if __name__ == "__main__":
    main()
