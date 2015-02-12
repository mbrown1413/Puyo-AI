Arduino code for controlling a gamecube playing Dr. Robotnik's Mean Bean
Machine.

This code works with the Arduino Uno, and probably the Duemilanove too. The
Leonardo has different pin mappings, so it won't work out of the box. You'll
either have to change the assembly code to use the correct pin, or move the
data wire to a different pin. Let me know if you have a different model Arduino
and I can help.


========= Setup =========

TODO

========= Resources =========

An Arduino based Gamecube to N64 controller converter. The assembly routines in
this file are taken from the Gamecube to N64 converter.
    https://github.com/brownan/Gamecube-N64-Controller

A lot of details on the protocol:
    http://www.int03.co.uk/crema/hardware/gamecube/gc-control.htm

An old archived page with a few details about the gamecube protocol:
    https://web.archive.org/web/20071025150150/http://www.gc-linux.org/docs/yagcd/chap9.html
