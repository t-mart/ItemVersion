# ItemVersion Changelog

## [2022.47.3] - 2022-11-24

- Use default profile by default, instead of a character specific one (#42)
- Add zhCN translation (#41)
- Add ruRU translation (#31)
- Add CMD key as a modifier for Mac clients (#38)

## [2022.47.2] - 2022-11-24

- Fix bugs in the last release that were present because of API differences between mainline and
  classic.

## [2022.47.1] - 2022-11-20

- Change tooltip format to `Added in <expac> (<version>)`. Before, was
  `Version: <version> Expansion: <expansion>`. This change emphasizes the expansion more, which is
  arguably more useful for most players.

- Add community updates mode, where some item's version is corrected to the one players
  expect. For example, Marrowroot was actually added in BfA, but only usable in SL. This option
  changes which version would be displayed in these cases.

- Add option for inclusion of community updates, which changes some items' version/expansion to the
  one that players expect. For example, the herb Marrowroot was actually added towards the end of
  BfA in pre-release development, but was only obtainable in SL.'

  With this option turned on, ItemVersion would report SL in this case, instead of BfA. Because the
  updates are non-canonical, the version number will be a placeholder one: the major part will be
  that of the new expansion, but the lesser parts will be zeroed.

  If you encounter an item that is not fixed by these updates, please consider "reporting it to the
  project page.

- Add requirement to press some key modifiers (Shift, Ctrl, Alt) to display ItemVersion in tooltip.

- Add options window with many things to configure. Access it with `/itemversion` or through the
  Blizzard Addon Options menu.

- Add profile management, so you can have different settings in different scenarios.

- In several places, custom text has been added, such as in the tooltip and in the options menu.
  Non-`enUS`-locale players will unfortunately see English text in these cases until translations
  have been completed. If you can help with this, please see the instructions at
  `ItemVersion/Locales/README.md`.

- Remove 3 second timer that attempted to place this addon's tooltip line last. This was a hack,
  and I don't feel like this addon deserves that last line any more than any other addon.

- Rewrite a lot of stuff using Ace libraries and some official WoW API.

## [2022.46.2] - 2022-11-20

- Use new Tooltip API for Dragonflight

## [2022.34.0] - 2022-08-23

### Added

- Added basic localization by minorly rewording tooltips to leverage translations that Blizzard
  provides. This enables non-English-locale players see the text in their own language.

## [2022.33.1] - 2022-08-16

### Changed

- Last release pulled because of some errors encountered with new build process. Should be good now.

## [2022.33.0] - 2022-08-16 [YANKED]

### Changed

- Update for Interface 9.2.7
- We're back. Too many things to list.

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
