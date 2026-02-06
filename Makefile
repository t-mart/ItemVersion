.PHONY: build dev clean

ALL: dev

clean:
# get rid of all build artifacts
	rm -rf .release

clean-cache:
# get rid of cached libs only
	rm -rf ItemVersion/Libs

build:
# development build using cached libs
	@echo Building ItemVersion for development
	./scripts/dev-build-with-cached-libs.sh

dev:
# start a loop that triggers a build on file changes in the ItemVersion directory
	watchexec --watch ItemVersion --restart make build
