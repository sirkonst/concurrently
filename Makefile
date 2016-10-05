OPEN = $(shell which xdg-open || which gnome-open || which open)

all: test

.PHONY: test
test:
	tox --recreate


.PHONY: build_doc
build_doc:
	make -C docs/ html


.PHONY: doc
doc: build_doc
	${OPEN} docs/_build/html/index.html
