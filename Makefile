SHELL = /bin/sh

ifeq ($(PREFIX),)
PREFIX = /usr/local
endif

ifeq ($(BINDIR),)
BINDIR = /bin
endif

ifeq ($(MANDIR),)
MANDIR = /share/man
endif

all:
install:
	install qr-backup $(DESTDIR)$(PREFIX)$(BINDIR)/qr-backup
	install -m 644 docs/qr-backup.1.man $(DESTDIR)$(PREFIX)$(MANDIR)/man1/qr-backup.1
uninstall:
	rm -f $(DESTDIR)$(PREFIX)$(BINDIR)/qr-backup
	rm -f $(DESTDIR)$(PREFIX)$(MANDIR)/man1/qr-backup.1
