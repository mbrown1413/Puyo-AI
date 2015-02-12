
#include "gc_com.h"
#include "gc_state_queue.h"

void GCStateQueue_clear(GCStateQueue* mq) {
    mq->len = 0;
    mq->pos = 0;
    mq->queue[0].state = gc_default_state;
}

void GCStateQueue_push(GCStateQueue* mq, const GCState* state, unsigned int count) {
    if(mq->len >= GC_STATE_QUEUE_MAX) {
        return;
    }
    memcpy((void*) &mq->queue[mq->len].state, (void*) state, sizeof(GCState));
    mq->queue[mq->len].count = count;
    mq->len++;
}

const GCState* GCStateQueue_peek(const GCStateQueue* mq) {
    if(mq->pos < 0 || mq->pos >= mq->len) {
        return &gc_default_state;
    }
    return &mq->queue[mq->pos].state;
}

const GCState* GCStateQueue_next(GCStateQueue* mq) {
    if(mq->pos >= mq->len) {
        GCStateQueue_clear(mq);
    } else {
        mq->queue[mq->pos].count--;
        if(mq->queue[mq->pos].count == 0) {
            mq->pos++;
        }
    }
    const GCState* state = GCStateQueue_peek(mq);
    return state;
}
