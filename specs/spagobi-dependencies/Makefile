PACKAGE_NAME=spagobi-dependencies
VERSION=5.2.0
MILESTONE=master
ifneq ($(MILESTONE),)
SUFFIX:=_$(MILESTONE)
endif
PACKAGE_VERSION=$(VERSION)$(SUFFIX)
PACKAGE_RPM_VERSION=$(VERSION)
PACKAGE_RPM_RELEASE=0.0.$(MILESTONE)

PREFIX=/usr/local
DATAROOTDIR=$(PREFIX)/share
JAVADIR=$(DATAROOTDIR)/java
POMDIR=$(DATAROOTDIR)/maven-poms
APPJAVADIR=$(JAVADIR)/$(PACKAGE_NAME)
APPPOMDIR=$(POMDIR)/$(PACKAGE_NAME)
OFFLINE=0

.SUFFIXES:
.SUFFIXES: .in .in.in

%.in.in%.in:

all:		\
		download \
		doc \
		$(NULL)

maintainer-clean:	dist-clean
	rm -fr downloads

dist-clean:	clean

clean:
	rm -f downloads/downloads.list
	rm -f spagobi-dependencies.spec
	rm -f COPYING
	rm -f COPYING.csv
	rm -f *.tmp

install:	all
	install -d -m 0755 "$(DESTDIR)$(APPJAVADIR)"
	install -d -m 0755 "$(DESTDIR)$(APPPOMDIR)"
	./install.sh downloads "$(DESTDIR)$(APPJAVADIR)" "$(DESTDIR)$(APPPOMDIR)"

.PHONY: spagobi-dependencies.spec.in.in
dist:		\
		download \
		spagobi-dependencies.spec \
		$(NULL)

	tar --files-from dist.list \
		--files-from downloads/downloads.list \
		conf.d/*.conf \
		--xform 's#^#$(PACKAGE_NAME)-$(PACKAGE_VERSION)/#' \
		-czf "$(PACKAGE_NAME)-$(PACKAGE_VERSION)-$(PACKAGE_RPM_RELEASE).tar.gz" \
		spagobi-dependencies.spec \
		$(NULL)

download:	downloads/downloads.list

downloads/downloads.list:	\
		conf.d/*.conf
	if [ "$(OFFLINE)" = 0 ]; then \
		./download.sh downloads; \
	fi

doc:		\
		COPYING \
		COPYING.csv \
		$(NULL)

COPYING:	\
		conf.d/*.conf
	./doc.sh COPYING

COPYING.csv:	\
		conf.d/*.conf
	./csv.sh COPYING.csv

spagobi-dependencies.spec:	spagobi-dependencies.spec.in
	sed \
		-e "s/@PACKAGE_LICENSE@/$$(./speclicense.sh)/g" \
		$< > $@

.in .in.in.in:
	sed \
		-e 's/@PACKAGE_NAME@/$(PACKAGE_NAME)/g' \
		-e 's/@PACKAGE_VERSION@/$(PACKAGE_VERSION)/g' \
		-e 's/@PACKAGE_RPM_VERSION@/$(PACKAGE_RPM_VERSION)/g' \
		-e 's/@PACKAGE_RPM_RELEASE@/$(PACKAGE_RPM_RELEASE)/g' \
		$< > $@

update-sha1sum:
	sha1sum --binary downloads/* > downloads.sha1
