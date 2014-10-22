
import serial

class GamecubeControl(object):

    def __init__(self, device):
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
