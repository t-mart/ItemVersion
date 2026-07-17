.PHONY: libs clean build install uninstall status check format locales test watch

SOURCE_DIR := ItemVersion
BUILD_ROOT := .release
BUILD_DIR := $(BUILD_ROOT)/$(SOURCE_DIR)
BUILD_LIBS_DIR := $(BUILD_DIR)/Libs
LIBS_DIR := $(SOURCE_DIR)/Libs
SOURCES := $(shell find ./$(SOURCE_DIR) -type f -not -path "./$(LIBS_DIR)*")

ALL: build

clean:
	rm -rf $(BUILD_ROOT)
	rm -rf $(LIBS_DIR)

$(BUILD_DIR): $(SOURCES)
	release.sh -ze

$(BUILD_LIBS_DIR):
	release.sh -z

$(LIBS_DIR): $(BUILD_LIBS_DIR)
	cp -r $(BUILD_LIBS_DIR) $(SOURCE_DIR)/

libs: $(LIBS_DIR)

build: $(BUILD_DIR)

# Make passes command-line and inherited env vars through to recipes, so
# `make install WOW_ROOT=...` reaches the script without any plumbing here.
install uninstall status check format locales test watch:
	@scripts/dev.sh $@
