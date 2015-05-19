
Arduino code for controlling a gamecube playing Dr. Robotnik's Mean Bean
Machine. The computer sends one-byte commands to the Arduino, which acts as a
Gamecube controller by implementing the Gamecube controller's wire protocol.

The AVR assembly routines are taken from the
[Gamecube-N64-Controller](https://github.com/brownan/Gamecube-N64-Controller)
project.


Setup
=====

Hardware
--------

 * **Arduino** - Uno or Duemilanove running at 16MHz. Other types may work with
   modifications to the software. For example, the Arduino Leonardo has
   different pin mappings between the microcontroller pins and the Arduino
   pins, so those will need to be modified. Let me know if you have a
   different model Arduino and I can help.
 * **Gamecube controller extension coord** - You only need the end that plugs
   into the Gamecube, the other end will be cut off.
 * **Gamecube** - duh.

Useful Tools:

 * Wire strippers
 * Electrical tape
 * Multimeter
 * Soldering iron and solder

Attach Gamecube to Arduino
--------------------------

Cut the Gamecube extension cable so there is enough slack on the end that
plugs into the Gamecube. Connect three of the wires to the Arduino as follows:

 * Brown - Ground
 * Yellow - Ground
 * Red (Signal) - Digital I/O 2

**TODO:** How to double check wire colors, diagram of connector pinout, and
instructions for figuring this out using a multimeter.

Program Arduino
---------------

Download the [Arduino IDE](http://www.arduino.cc/en/Main/Software), then open
[gamecube_control.ino](gamecube_control.ino). After connecting the Arduino via
a USB cable, select the Arduino model and serial port from the tools menu.
The serial port will be something like `/dev/ttyACM0` or `/dev/ttyUSB0`
depending on the model of Arduino you have. Click the upload icon to compile
and upload the code.

Test it
-------

Make sure the Arduino is plugged into the Gamecube, then start up your
favorate game. Try out some button presses using the `gc_send.py` command, for
example:

    $ python gc_send.py /dev/ttyUSB0 start

If you navigate yourself to a game of Puyo Puyo, you can make a complete move
in a single command by specifying a column number and a number of clockwise
rotations:

    $ python gc_send.py /dev/ttyUSB0 0,3


Resources
=========

 * [Gamecube-N64-Controller](https://github.com/brownan/Gamecube-N64-Controller) - An Arduino based Gamecube to N64 controller converter.
 * [Nintendo Gamecube Controller Protocol](http://www.int03.co.uk/crema/hardware/gamecube/gc-control.htm) - A lot of details on the Gamecube protocol.
 * [Yet Another Gamecube Documentation](https://web.archive.org/web/20071025150150/http://www.gc-linux.org/docs/yagcd/chap9.html) - An old archived page with a few details about the Gamecube protocol.
