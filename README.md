# ItemVersion

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/t-mart/ItemVersion)](https://github.com/t-mart/ItemVersion/releases)
[![Release](https://github.com/t-mart/ItemVersion/actions/workflows/release.yml/badge.svg)](https://github.com/t-mart/ItemVersion/actions/workflows/release.yml)
[![GitHub issues](https://img.shields.io/github/issues/t-mart/ItemVersion)](https://github.com/t-mart/ItemVersion/issues)
[![License on GitHub](https://img.shields.io/github/license/t-mart/ItemVersion)](https://github.com/t-mart/ItemVersion/blob/master/LICENSE)
[![Packaged by wap](https://img.shields.io/badge/packaged%20by-wap-d33682)](https://github.com/t-mart/wap)
[![Hosted on Curseforge](https://img.shields.io/badge/hosted%20on-CurseForge-F16436)](https://www.curseforge.com/wow/addons/itemversion)

![Montage](https://i.imgur.com/9PVkwkz.png)

**ItemVersion adds information to your tooltip about when an item was added to World of Warcraft.**

## Useful for

- Clearing your bags and bank of old stuff
- Identifying loot from your transmog runs
- Looking back on WoW history

## Features

- A complete database of when every item was added to the game, in `<major>.<minor>.<patch>.<build>`
  format and with expansion name, such as `Version: 9.0.1.36216, Expac: Shadowlands`.
- Where-you-need-it accessibility in the item tooltip.
- Lua API exposed for use by other addons.
- Weekly updates with the latest items. A refreshed release will automatically occur (at least)
  every Tuesday at 16:00 UTC, just slightly after reset.
- Open source visibility.

## Usage

Just install the addon like normal and mouse over any item!

## API

See the [API page](https://github.com/t-mart/ItemVersion/blob/master/docs/API.md)

## Support

- **I think an item has the wrong version.**

  First, verify it on [wowhead.com](https://www.wowhead.com/). If Wowhead _does_ in fact disagree
  with the data in ItemVersion, please create a GitHub issue.

  Often, items are added towards the end of an expansion that actually used in the _next_ expansion,
  making them appear to have too early of a version. Unfortunately, there's not much we can do in
  these cases -- the canonical version is better than making something up.

- **An item actually is misversioned** or **An item is missing** or **I found a bug** or **I want to
  request a feature.**

  Create an [issue on the GitHub project page](https://github.com/t-mart/ItemVersion/issues)

- **I want to submit a change**

  Fork the project and make a [pull request](https://github.com/t-mart/ItemVersion/pulls)!

## License

Copyright 2022 Tim Martin

Licensed under the GPLv3:
[https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html)
