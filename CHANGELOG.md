# ItemVersion Changelog

This file keeps track of changes to ItemVersion over time. For each release, there will be at most
three sections: Added, Fixed, and Changed

Every week, a data refresh release of this project occurs. These releases will not be documented
here because it is an automated process.

## [2021.11.3] - 2021-03-18

### Fixed

- Use new wap v0.8.1 options in CI workflow

## [2021.11.2] - 2021-03-18 [YANKED]

### Changed

- Bump Interface version to 9.0.5
- Upgrade CI workflow for wap 0.8.1

## [2021.8.3] - 2021-02-28

### Added

- When an item's version cannot be found, print a helpful error
- A slash command, `/itemversion`, that prints out the version of the addon

### Fixed

- Make item id extraction from tooltip links more robust

### Changed

- Upgrade CI workflow for wap 0.7.1

## [2021.8.2] - 2021-02-24

### Fixed

- Use tagged version in CI workflow

## [2021.8.1] - 2021-02-24

### Fixed

- Fixed luacheck errors

### Added

- This changelog!
- Added luacheck to project

### Changed

- Started using [wap](https://github.com/t-mart/wap) packaging in CI flow
