
all: puyo

puyo:
	$(MAKE) -C puyo/

clean:
	$(MAKE) -C puyo/ clean

.PHONY: all puyo clean
