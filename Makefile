SHELL = /bin/sh
# The following line requires GNU make
VERSION := $(subst ",,$(subst VERSION = ,,$(shell grep "VERSION =" qr-backup)))

ifeq ($(PREFIX),)
PREFIX = /usr/local
endif

ifeq ($(BINDIR),)
BINDIR = /bin
endif

ifeq ($(MANDIR),)
MANDIR = /share/man
endif

none:
all: dist/qr-backup-${VERSION}.tar.gz dist/qr-backup-${VERSION}.tar.gz.sig
dist/qr-backup-${VERSION}.tar.gz: docs font src tests Makefile qr-backup requirements.txt
	mkdir -p dist/qr-backup-${VERSION}
	cp -rt dist/qr-backup-${VERSION} $^
	cd dist && tar cf qr-backup-${VERSION}.tar qr-backup-${VERSION}
	rm -f $@
	gzip -9 dist/qr-backup-${VERSION}.tar
dist/qr-backup-${VERSION}.tar.gz.sig: dist/qr-backup-${VERSION}.tar.gz
	gpg --detach-sign --armor -o $@ $<
deb: dist/qr-backup-${VERSION}.tar.gz
	mkdir -p dist/debian
	cp dist/qr-backup-${VERSION}.tar.gz dist/debian/qr-backup_${VERSION}.orig.tar.gz
	cd dist/debian && tar xf qr-backup_${VERSION}.orig.tar.gz
	cp -lr package/debian dist/debian/qr-backup-${VERSION}/debian
	cd dist/debian/qr-backup-${VERSION} && debuild -us -uc
clean:
	rm -rf dist deb_test
install:
	install -D qr-backup $(DESTDIR)$(PREFIX)$(BINDIR)/qr-backup
	install -D -m 644 docs/qr-backup.1.man $(DESTDIR)$(PREFIX)$(MANDIR)/man1/qr-backup.1
uninstall:
	rm -f $(DESTDIR)$(PREFIX)$(BINDIR)/qr-backup
	rm -f $(DESTDIR)$(PREFIX)$(MANDIR)/man1/qr-backup.1
