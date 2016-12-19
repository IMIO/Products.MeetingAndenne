#!/usr/bin/make
#
all: run

.PHONY: bootstrap
bootstrap:
	/srv/python/python2711/bin/virtualenv --no-site-packages .
	./bin/python bootstrap.py --version 1.7.1

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -v

.PHONY: run
run:
	if ! test -f bin/instance;then make buildout;fi
	bin/instance fg

.PHONY: cleanall
cleanall:
	rm -fr develop-eggs downloads eggs parts .installed.cfg .mr.developer.cfg
