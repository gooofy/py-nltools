SHELL := /bin/bash

all:	doc

doc:	README.adoc
	asciidoctor -r asciidoctor-diagram README.adoc

clean:
	./ai_cli.py clean -a all
