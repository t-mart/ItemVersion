.PHONY: dev-build watch clean

ALL: watch

clean:
# get rid of all build artifacts
	rm -rf .release

clean-cache:
# get rid of cached libs only
	rm -rf ItemVersion/Libs

dev-build:
# development build using cached libs
	@echo Building ItemVersion for development
	./scripts/dev-build-with-cached-libs.sh

watch:
# start a loop that triggers a dev-build on file changes in the ItemVersion directory
	watchexec --watch ItemVersion --restart make dev-build
