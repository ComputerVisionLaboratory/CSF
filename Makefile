.PHONY: docs
docs: 
	nbdev_clean_nbs
	nbdev_build_lib
	nbdev_build_docs
	touch docs

pull-image:
	docker pull fastdotai/nbdev-dev:latest

docs_serve: docs
	cd docs && bundle exec jekyll serve
