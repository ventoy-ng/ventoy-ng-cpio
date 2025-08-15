srcdir ?= ..
prefix ?= /usr/local
DESTDIR ?=

O := obj

$(shell mkdir -p $(O))

VPATH := $(O) $(addprefix $(srcdir)/,linux/lib/xz userspace)

CROSS ?=
CC := $(CROSS)cc
STRIP := $(CROSS)strip

CFLAGS := -Oz
BCJ_CPPFLAGS = -DXZ_DEC_X86 -DXZ_DEC_ARM -DXZ_DEC_ARMTHUMB -DXZ_DEC_ARM64 \
	-DXZ_DEC_RISCV -DXZ_DEC_POWERPC -DXZ_DEC_IA64 -DXZ_DEC_SPARC
CPPFLAGS = -DXZ_USE_CRC64 -DXZ_USE_SHA256 -DXZ_DEC_ANY_CHECK \
	-DXZ_DEC_CONCATENATED
LDFLAGS := -static

ALL_CFLAGS := $(CFLAGS) -pedantic -Wall -Wextra -Wdeclaration-after-statement \
	-MMD
ALL_CPPFLAGS := $(CPPFLAGS) $(BCJ_CPPFLAGS) \
	$(addprefix -I$(srcdir)/, linux/include/linux userspace)

BIN := xzminidec

xzminidec_deps := xzminidec.c \
	xz_crc32.c xz_crc64.c \
	xz_dec_stream.c xz_dec_lzma2.c xz_dec_bcj.c \
	xz_sha256.c

all: $(BIN)

-include $(O)/%.d

clean:
	-rm -r $(O)

$(O)/xzminidec: $(addprefix $(O)/, xzminidec.o $(xzminidec_deps:.c=.o))
	$(CC) -o $@ $^ $(ALL_CFLAGS) $(LDFLAGS)

$(O)/%.o: %.c
	$(CC) -o $@ $< -c $(ALL_CFLAGS) $(ALL_CPPFLAGS)

install:
	@mkdir -p $(DESTDIR)
	cp $(O)/xzminidec $(DESTDIR)/xzminidec
	$(STRIP) --strip-all $(DESTDIR)/xzminidec
