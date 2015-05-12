<style>
    table, td, th {
        text-align: center;
        border: 1px black solid;
    }
</style>

This documents commands sent to the Arduino via Serial.

Commands
========

Every command is one byte. The first bits determine which command to execute. The meaning of the remaining bits are determined by the command.

Command Summary:
<table>
    <tr>
        <th rowspan=2>Command</th>
        <th colspan=8>Bit</th>
    </tr>
    <tr>
        <th>0</th>
        <th>1</th>
        <th>2</th>
        <th>3</th>
        <th>4</th>
        <th>5</th>
        <th>6</th>
        <th>7</th>
    </tr>
    <tr>
        <td>Puyo Move</td>
        <td>0</td>
        <td>0</td>
        <td colspan=3>X movement</td>
        <td colspan=2>Rotation</td>
        <td>Down Fast</td>
    </tr>
    <tr>
        <td>Single Button</td>
        <td>0</td>
        <td>1</td>
        <td colspan=4>Button</td>
        <td colspan=2>Repetitions</td>
    </tr>
</table>


Puyo Move
---------

Move a falling pair of pieces left-to-right and rotate them.

Command bits: 0b00

Fields:

<table>
    <tr>
        <th>Field</th>
        <th>N Bits</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>X movement</td>
        <td>3</td>
        <td>Number of times to move the pieces left/right, zeroed at 2. 0 means move left twice, 2 means no movement, 4 means move 2 right, etc.</td>
    </tr>
    <tr>
        <td>Rotation</td>
        <td>2</td>
        <td>Number of times the pieces should be rotated clockwise</td>
    </tr>
    <tr>
        <td>Down Fast</td>
        <td>1</td>
        <td>If 1, the pieces will be dropped quickly after the move is finished by holding down.</td>
    </tr>
</table>

Single Button
-------------

Press a single button (or joystick direction) one or more times.

Command bits: 0b01

Fields:

<table>
    <tr>
        <th>Field</th>
        <th>N Bits</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>Button</td>
        <td>4</td>
        <td>Which button to push. See the table below for the mapping between these values and the buttons.</td>
    </tr>
    <tr>
        <td>Repetitions</td>
        <td>2</td>
        <td>Number of times to repeat the button press</td>
    </tr>
</table>

Button Values:
<table>
    <tr><th>Value</th><th>Button</th></tr>
    <tr><td>0x0</td><td>Start</td></td>
    <tr><td>0x1</td><td>Joystick Up</td></td>
    <tr><td>0x2</td><td>Joystick Down</td></td>
    <tr><td>0x3</td><td>A</td></td>
    <tr><td>0x4</td><td>B</td></td>
    <tr><td>0x5</td><td>X</td></td>
    <tr><td>0x6</td><td>Y</td></td>
    <tr><td>0x7</td><td>Left Trigger</td></td>
    <tr><td>0x8</td><td>Right Trigger</td></td>
    <tr><td>0x9</td><td>Joystick Left</td></td>
    <tr><td>0xA</td><td>Joystick Right</td></td>
</table>
