.PHONY: libs clean build

SOURCE_DIR := ItemVersion
BUILD_ROOT := .release
BUILD_DIR := $(BUILD_ROOT)/$(SOURCE_DIR)
BUILD_LIBS_DIR := $(BUILD_DIR)/Libs
LIBS_DIR := $(SOURCE_DIR)/Libs
SOURCES := $(shell find ./$(SOURCE_DIR) -type f -not -path "./$(LIBS_DIR)*")
# DEV_LOCALES := $(SOURCE_DIR)/DevLocales.lua
# TEMP_DIR := .temp
# LATEST_GITHUB_RELEASE_ZIP_URL := https://github.com/t-mart/ItemVersion/releases/latest/download/ItemVersion.zip

ALL: build

clean:
	rm -rf $(BUILD_ROOT)
	rm -rf $(LIBS_DIR)
	rm -rf $(TEMP_DIR)
	rm -rf $(DEV_LOCALES)

$(BUILD_DIR): $(SOURCES)
	release.sh -ze

$(BUILD_LIBS_DIR):
	release.sh -z

$(LIBS_DIR): $(BUILD_LIBS_DIR)
	cp -r $(BUILD_LIBS_DIR) $(SOURCE_DIR)/

# $(DEV_LOCALES):
# # download the latest release to temp (a zip file) and extract
# # ItemVersion/DevLocales.lua from it and copy it to the source directory
# 	mkdir -p $(TEMP_DIR)
	

libs: $(LIBS_DIR)

build: $(BUILD_DIR)
