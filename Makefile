.PHONY: deps

deps:
	git submodule update --init --recursive
	uv sync
