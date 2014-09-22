
CFLAGS+=--std=c99 -Werror -Wall -pedantic
#CFLAGS+=-g
CFLAGS+=-O3

SOURCES=$(wildcard src/*.c)

all: libpuyo.so

libpuyo.so: $(SOURCES)
	$(CC) -I./src/ $(CFLAGS) -fPIC -Wl,-soname,$@ --shared $(SOURCES) -o $@

clean:
	-rm libpuyo.so

.PHONY: all clean
