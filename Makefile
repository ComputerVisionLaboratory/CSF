.ONESHELL:
SHELL := /bin/bash
SRC = $(wildcard nbs/*.ipynb)


NB_PORT = 8080
DOCS_PORT = 4000
CVAT_PORT = 8081
CVAT_PATH = "~/ball_detection/submodules/cvat"
up: 
	NB_PORT=$(NB_PORT) DOCS_PORT=$(DOCS_PORT) CVAT_PORT=$(CVAT_PORT) CVAT_PATH=$(CVAT_PATH) \
	docker-compose -f .docker/docker-compose.yml up \
	--build  

connect-ports:
	

bye:
	echo "bye world"

dockerfile:
	docker build -t atomscott/conda -f .docker/Dockerfile . 

attach:
	docker run -v /home/atom/ball_detection/:/ws/ -it atomscott/conda /bin/zsh

all: RSF docs

RSF: $(SRC)
	nbdev_build_lib
	touch RSF

sync:
	nbdev_update_lib

docs_serve: docs
	cd docs && bundle exec jekyll serve

.PHONY: docs
docs: 
	nbdev_clean_nbs
	nbdev_build_lib
	nbdev_build_docs
	touch docs

test:
	nbdev_test_nbs

release: pypi conda_release
	nbdev_bump_version

conda_release:
	fastrelease_conda_package

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist
