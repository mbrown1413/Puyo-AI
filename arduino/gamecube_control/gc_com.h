
#ifndef _GC_COM_H
#define _GC_COM_H

// 8 bytes of data that we send to the GC, in packed format ready to push onto
// the wire.
typedef struct {
    // bits: 0, 0, 0, start, y, x, b, a
    unsigned char data1;
    // bits: 1, L, R, Z, Dup, Ddown, Dright, Dleft
    unsigned char data2;
    unsigned char stick_x;  // 128 is center for stick and cstick
    unsigned char stick_y;
    unsigned char cstick_x;
    unsigned char cstick_y;
    unsigned char left;  // left/right trigger analog
    unsigned char right;
} GCState;

static const GCState gc_default_state = {0, 0, 128, 128, 128, 128, 0, 0};

void gc_setup();
void gc_send(unsigned char *buffer, char length);
int gc_recv(unsigned char *bitbin);

#endif
