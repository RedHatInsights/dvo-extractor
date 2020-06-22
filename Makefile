.PHONY: pycco

SOURCES:=$(shell find . -name '*.py')
DOCFILES:=$(addprefix docs/packages/, $(addsuffix .html, $(basename ${SOURCES})))

default: pycco

docs/packages/%.html: %.py
	mkdir -p $(dir $@)
	pycco -d $(dir $@) $^

pycco: ${DOCFILES}
