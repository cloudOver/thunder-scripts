all:
	mkdir -p $(DESTDIR)/usr/bin/
	python3 setup.py install --root=$(DESTDIR)
	cp -r bin/* $(DESTDIR)/usr/bin/
	chmod a+x $(DESTDIR)/usr/bin/*
