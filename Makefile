.PHONY: docs
docs: 
	nbdev_clean_nbs
	nbdev_build_lib
	nbdev_build_docs
	touch docs