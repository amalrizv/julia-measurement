
CC:=gcc
LD:=ld
AR:=ar
CFLAGS:=-Wall -O2 -pthread
LDFLAGS:=


all: pt_ctx_switch pt_create


pt_ctx_switch: pt_ctx_switch.c common.h
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

pt_create: pt_create.c common.h
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

clean:
	@rm -f pt_ctx_switch pt_create *.o


.PHONY: clean