all:
	echo Nothing to compile

install:
	mkdir -p $(DESTDIR)/usr/sbin/
	python setup.py install --root=$(DESTDIR)
	cp -r sbin/* $(DESTDIR)/usr/bin/
	chmod a+x $(DESTDIR)/usr/bin/

egg:
	python setup.py sdist bdist_egg

egg_install:
	python setup.py install

egg_upload:
	# python setup.py sdist bdist_egg upload
	python setup.py sdist upload

egg_clean:
	rm -rf build/ dist/ thunderscript.egg-info/

egg_deploy:
	scp -r . $(DEPLOY_HOST):corecluster
	ssh $(DEPLOY_HOST) "pip uninstall --yes corecluster" || true
	ssh $(DEPLOY_HOST) "cd corecluster ; make egg"
	ssh $(DEPLOY_HOST) "cd corecluster ; make egg_install"
