
#include "gc_com.h"
#include "gc_state_queue.h"


// Response to the identify (0x00) command
// Some of the meaning of this response is described here:
//   https://web.archive.org/web/20071025150150/http://www.gc-linux.org/docs/yagcd/chap9.html
static unsigned char identify_response[] = {0x09, 0x00, 0x20};

// Response to the origins (0x41) command
// Not sure what these bits mean, but this is a response I sniffed from my
// controller.
static unsigned char origin_response[] = {
    0x00, 0x80, 0x7d, 0x87, 0x82,
    0x85, 0x1f, 0x22, 0x00, 0x00
};


static GCState gc_state = gc_default_state;
static GCStateQueue state_queue;
unsigned int i = 0;


void setup() {
    gc_setup();
    Serial.begin(115200);
    GCStateQueue_clear(&state_queue);
}

void loop() {
    int ret;
    unsigned char from_gc;

    do {
        ret = gc_recv(&from_gc);
    } while (ret != 1);

    switch(from_gc) {

        case 0x00:  // Identify Command
            gc_send(identify_response, sizeof(identify_response));
        break;

        case 0x41:  // Origin Command
            delayMicroseconds(4);  // Not sure why this is needed
            gc_send(origin_response, sizeof(origin_response));
        break;

        case 0x40:  // Read Command

            // Delay until the gamecube is listening
            // We are receiving 24 bits plus a stop bit, so 25 bits total, but
            // we've already received 8 of them. We must wait until the
            // gamecube is done sending. Each bit takes 4 microseconds, so
            // we'll wait 4*17 plus a little extra to give the gamecube a
            // chance to wait for our response.
            delayMicroseconds(4*17 + 28);

            gc_send((unsigned char*) &gc_state, sizeof(gc_state));
        break;

        //default:  // Unknown
        //    Serial.println(from_gc, HEX);

    }

    if(Serial.available()) {
        process_serial_command(Serial.read(), &state_queue);
        gc_state = *GCStateQueue_peek(&state_queue);
        i = 0;

    //TODO: Why every 5 times? Does 4 work? Does 1?
    } else if(i % 5 == 0) {
        gc_state = *GCStateQueue_next(&state_queue);
    }

    i++;
}

/**
 * Adds controller states to the queue based on the command.
 */

static void process_serial_command(unsigned char c, GCStateQueue* queue) {
    switch((c & 0xC0) >> 6) {
        case 0x0:
            process_serial_command_puyo_move(c, queue);
        break;
        case 0x1:
            process_serial_command_single_button(c, queue);
        break;
    }
}

static void process_serial_command_puyo_move(unsigned char c, GCStateQueue* queue) {
    GCState tmp_state = gc_default_state;

    int delta_x = ((c & 0x38) >> 3) - 2;  // Amount to move left/right
    int rot = (c & 0x06) >> 1;  // Num clockwise rotations
    bool down_fast = (c & 0x01);  // Hold down afterward?

    GCStateQueue_clear(queue);

    do {

        if(delta_x > 0) {
            tmp_state.stick_x = 255;
            delta_x--;
        } else if(delta_x < 0) {
            tmp_state.stick_x = 0;
            delta_x++;
        }

        switch(rot) {
            case 1:
            case 2:
                tmp_state.data1 |= 0x04;  // Press X (rotate clockwise)
                rot--;
            break;
            case 3:
                tmp_state.data1 |= 0x01;  // Press A (rotate anticlockwise)
                rot = 0;
            break;
        }

        GCStateQueue_push(queue, &tmp_state, 1);

        // Clear controller
        tmp_state = gc_default_state;
        if(delta_x != 0 || rot != 0) {
            GCStateQueue_push(queue, &tmp_state, 1);
        }

    } while(delta_x != 0 || rot != 0);

    if(down_fast) {
        tmp_state.stick_y = 0;
        GCStateQueue_push(queue, &tmp_state, 8);
    }

    // Clear controller one last time
    tmp_state = gc_default_state;
    GCStateQueue_push(queue, &tmp_state, 1);

}

static void process_serial_command_single_button(unsigned char c, GCStateQueue* queue) {
    GCState new_state = gc_default_state;

    int button = (c & 0x3C) >> 2;
    int repetitions = (c & 0x03) + 1;

    switch(button) {
        case 0x0: new_state.data1 |= 0x10; break;  // Start
        case 0x1: new_state.stick_y = 255; break;  // Up
        case 0x2: new_state.stick_y = 0;   break;  // Down
        case 0x3: new_state.data1 |= 0x01; break;  // A
        case 0x4: new_state.data1 |= 0x02; break;  // B
        case 0x5: new_state.data1 |= 0x04; break;  // X
        case 0x6: new_state.data1 |= 0x08; break;  // Y
        case 0x7: break;  // TODO: Left trigger not implemented
        case 0x8: break;  // TODO: Left trigger not implemented
        case 0x9: new_state.stick_x = 0;   break;  // Left
        case 0xA: new_state.stick_x = 255; break;  // Right
        case 0xB: new_state.data2 |= 0x10; break;  // Z
    }

    for(int i=0; i<repetitions; i++) {
        GCStateQueue_push(queue, &new_state, 1);
        GCStateQueue_push(queue, &gc_default_state, 1);
    }

}
