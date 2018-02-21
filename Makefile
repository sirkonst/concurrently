# interpreter version (ex.: 3.6) or use current
PYTHON := $(PYTHON)
OPEN = $(shell which xdg-open || which gnome-open || which open)

all: test

.PHONY: test
test:
	if [ -z "$(PYTHON)" ]; then \
	    tox --recreate --skip-missing-interpreters; \
	else \
	    tox --recreate -e py$(PYTHON); \
	fi;

.PHONY: build_doc
build_doc:
	make -C docs/ html


.PHONY: doc
doc: build_doc
	${OPEN} docs/_build/html/index.html


.PHONY: install
install:
	pip install  .


.PHONY: install_dev
install_dev:
	pip install --editable .[develop]
