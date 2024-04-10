help:
	@echo "make <tab> for targets"
.PHONY: help

pytest:
	pytest -n 4 ./test_db4hls.py
.PHONY: pytest

ultraclean:
	rm -f workspace/dense/*tar.gz
	rm -rf workspace/dense/i_*
.PHONY: ultraclean
