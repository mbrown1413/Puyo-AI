
import serial


class Controller(object):
    """Controls a game system.

    Abstract for a class that can actually control the game by acting as a
    controller. A concrete implementation could, for example, send serial
    commands to a microcontroller that speaks the gamesystem's physical
    controller protocol.

    """

    def puyo_move(self, pos, rot, down_fast=True):
        """
        Drop a puyo at `pos` with rotation `rot`. If `down_fast` is True, hold
        down after the move is made to drop the puyo quickly.

        Note that `pos` does not directly correlate to how many times the puyos
        should be moved left or right. For example: if `pos` and `rot` are (0,
        0), the puyos will be moved left twice to be put in the first column;
        if `pos` and `rot` are (0, 3), the puyos will be moved left only once
        after rotation, since the center of rotation is the bottom puyo.
        """
        raise NotImplementedError("This method must be implemented by a "
                                  "subclass.")


class GamecubeController(Controller):

    def __init__(self, device):
        """
        Args:
            device: Serial device name of the arduino programmed to interact
                with the Gamecube. On Linux this might be something like
                "/dev/ttyACM0" or "/dev/ttyUSB0".
        """
        self.gc_dev = serial.Serial(device, 115200, timeout=0.01)

    def __del__(self):
        self.gc_dev.close()

    def puyo_move(self, pos, rot, down_fast=True):
        rot = rot % 4
        if pos > 5 or pos < 0:
            raise ValueError("`pos` must be between 0 and 5 inclusive")

        # If we're rotated anticlockwise, the game puts the pair one away from
        # the left side. Correct for that here.
        if rot == 3:
            pos += 1

        pos_bits = pos << 3
        rot_bits = rot << 1
        down_fast_bits = 0x1 if down_fast else 0x0

        command = pos_bits | rot_bits | down_fast_bits
        self.gc_dev.write(chr(command))
