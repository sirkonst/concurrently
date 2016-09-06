

all: test

.PHONY: test
test:
	tox --recreate
