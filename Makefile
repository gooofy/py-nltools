all:	README.html README.md dist

SHELL := /bin/bash

%.html: %.adoc
	asciidoctor -r asciidoctor-diagram -a toc $<

README.md: README.adoc
	asciidoc -b docbook README.adoc
	iconv -t utf-8 README.xml | pandoc -f docbook -t markdown_strict | iconv -f utf-8 > README.md

tests:
	nosetests

dist:	README.md
	python setup.py sdist
	python setup.py bdist_wheel --universal

upload:
	twine upload dist/*

clean:
	rm -f *.html *.png 
	rm -rf dist build  py_nltools.egg-info  README.md  README.xml 
