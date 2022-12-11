.PHONY = all

all = check

check:
	luacheck ItemVersion --no-color --exclude-files 'ItemVersion/Libs/**/*.lua' --no-self
