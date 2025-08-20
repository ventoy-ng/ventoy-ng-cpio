srcdir ?= ..
prefix ?= /usr/local
DESTDIR ?=

O := obj

$(shell mkdir -p $(O))

VPATH := $(O) $(srcdir) $(srcdir)/BabyISO

CROSS ?=
CC := $(CROSS)cc
STRIP := $(CROSS)strip

CFLAGS ?= -Oz
BASE_CPPFLAGS := -D_FILE_OFFSET_BITS=64 -DBUILD_VTOY_TOOL
CPPFLAGS ?=
LDFLAGS := -static

ALL_CFLAGS := $(CFLAGS) -Wall -MMD
ALL_CPPFLAGS := $(CPPFLAGS) $(BASE_CPPFLAGS) \
	-I$(srcdir) -I$(srcdir)/BabyISO

BIN := vtoytool

vtoytool_deps := vtoydm.c vtoydump.c vtoyexpand.c vtoykmod.c vtoyksym.c vtoyloader.c vtoytool.c vtoyvine.c \
	biso_9660.c biso.c biso_dump.c biso_eltorito.c biso_joliet.c biso_list.c biso_plat_linux.c biso_rockridge.c biso_util.c

all: $(BIN)

-include $(O)/%.d

clean:
	-rm -r $(O)

$(O)/vtoytool: $(addprefix $(O)/, vtoytool.o $(vtoytool_deps:.c=.o))
	$(CC) -o $@ $^ $(ALL_CFLAGS) $(LDFLAGS)

$(O)/%.o: %.c
	$(CC) -o $@ $< -c $(ALL_CFLAGS) $(ALL_CPPFLAGS)

install:
	@mkdir -p $(DESTDIR)
	cp $(O)/vtoytool $(DESTDIR)/vtoytool
	$(STRIP) --strip-all $(DESTDIR)/vtoytool
