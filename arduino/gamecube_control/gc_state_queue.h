
#ifndef _GC_STATE_QUEUE_H
#define _GC_STATE_QUEUE_H

static const int GC_STATE_QUEUE_MAX = 10;

typedef struct {
    struct {
        GCState state;
        unsigned int count;
    } queue[GC_STATE_QUEUE_MAX];
    int len;
    int pos;
} GCStateQueue;

void GCStateQueue_clear(GCStateQueue* mq);
void GCStateQueue_push(GCStateQueue* mq, const GCState* state, unsigned int count);
const GCState* GCStateQueue_peek(const GCStateQueue* mq);
const GCState* GCStateQueue_next(GCStateQueue* mq);

#endif
