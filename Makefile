.PHONY: deps protos

PROTO_SOURCE_DIR=falcon-protos
PROTO_BUILD_DIR=src/generated

PROTO_SRC := $(shell find $(PROTO_SOURCE_DIR) -name "*.proto")
BETTER_PROTO_PLUGIN=$(shell find .venv -name protoc-gen-python_betterproto2\*)

export PATH := $(shell pwd)/.venv/bin:$(PATH)

deps:
	git submodule update --init --recursive
	uv sync

protos:
	rm -rf $(PROTO_BUILD_DIR)
	mkdir -p $(PROTO_BUILD_DIR)

	protoc \
    --plugin=protoc-gen-python_betterproto2=$(BETTER_PROTO_PLUGIN) \
    -I=$(PROTO_SOURCE_DIR) \
    --python_betterproto2_out=$(PROTO_BUILD_DIR) \
    $(PROTO_SRC)