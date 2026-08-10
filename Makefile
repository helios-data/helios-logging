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

TEMP_PROTO_SOURCE_DIR=temp-protos
TEMP_PROTO_BUILD_DIR=src/generated_temp
TEMP_PROTO_SRC := $(shell find $(TEMP_PROTO_SOURCE_DIR) -name "*.proto")

.PHONY: temp-protos
temp-protos:
	rm -rf $(TEMP_PROTO_BUILD_DIR)
	mkdir -p $(TEMP_PROTO_BUILD_DIR)

	protoc \
	--plugin=protoc-gen-python_betterproto2=$(BETTER_PROTO_PLUGIN) \
	-I=$(TEMP_PROTO_SOURCE_DIR) \
	--python_betterproto2_out=$(TEMP_PROTO_BUILD_DIR) \
	$(TEMP_PROTO_SRC)