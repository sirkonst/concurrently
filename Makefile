# interpreter version (ex.: 3.6) or use current
PYTHON := $(PYTHON)
OPEN = $(shell which kde-open || which xdg-open || which gnome-open || which open)

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
	pip install --editable .[develop,gevent]


.PHONY: clean_dist
clean_dist:
	if [ -d dist/ ]; then rm -rv dist/; fi;


.PHONY: build_dist
build_dist: clean_dist
	python setup.py sdist bdist_wheel


.PHONY: _check_dist
_check_dist:
	test -d dist/ || ( \
		echo -e "\n--> [!] run 'make build_dist' before!\n" && exit 1 \
	)


.PHONY: upload
upload: _check_dist
	twine upload --skip-existing dist/*
