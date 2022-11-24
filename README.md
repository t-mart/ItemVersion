# ItemVersion

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/t-mart/ItemVersion)](https://github.com/t-mart/ItemVersion/releases)
[![Release](https://github.com/t-mart/ItemVersion/actions/workflows/release.yml/badge.svg)](https://github.com/t-mart/ItemVersion/actions/workflows/release.yml)
[![GitHub issues](https://img.shields.io/github/issues/t-mart/ItemVersion)](https://github.com/t-mart/ItemVersion/issues)
[![License on GitHub](https://img.shields.io/github/license/t-mart/ItemVersion)](https://github.com/t-mart/ItemVersion/blob/master/LICENSE)
[![Packaged by wap](https://img.shields.io/badge/packaged%20by-wap-d33682)](https://github.com/t-mart/wap)
[![Hosted on Curseforge](https://img.shields.io/badge/hosted%20on-CurseForge-F16436)](https://www.curseforge.com/wow/addons/itemversion)

![Hero](https://raw.githubusercontent.com/t-mart/ItemVersion/master/docs/images/hero.png)

**ItemVersion adds information to your tooltip about when an item was added to World of Warcraft.**

## Useful for

- Clearing your bags and bank of old stuff
- Identifying loot from your transmog runs
- Looking back on WoW history

## Features

- A complete database of the version/expansion in which every item was added.
- Where-you-need-it accessibility in the item tooltip.
- Weekly updates with the latest items. A refreshed release will automatically occur (at least)
  every Tuesday at 16:00 UTC, just slightly after reset.
- API exposed for use by other addons.
- Open source visibility.

## Usage

Just install the addon like normal and mouse over any item!

Access the options screen with `/itemversion`.

![Options screen](https://raw.githubusercontent.com/t-mart/ItemVersion/master/docs/images/options.png)

## API

See the [API page](https://github.com/t-mart/ItemVersion/blob/master/docs/API.md)

## Support

- **An item has the wrong version.**

  First, verify it on [wowhead.com](https://www.wowhead.com/). If Wowhead _does_ in fact disagree
  with the data in ItemVersion, please create a GitHub issue.

  In some cases, items are added towards the end of an expansion that actually used in the _next_
  expansion, making them appear to have too early of a version. For example,
  [Marrowroot](https://www.wowhead.com/item=168589/marrowroot), a herb used in Shadowlands, was
  actually added to the game during the previous expansion, Battle for Azeroth. And, ItemVersion
  will display Battle for Azeroth because it is canonically correct.

  However, to instead display the expansion that players probably expect in these cases, turn on the
  "Include community updates" option on the options screen. Then, the Marrowroot example would
  display Shadowlands.

  (These community updates are an ongoing effort. If you have discovered an item that's usage is in
  a different expansion than ItemVersion reports, please lend a hand and create an
  [issue on the GitHub project page](https://github.com/t-mart/ItemVersion/issues).

- **An item still has the wrong version** or **An item is missing** or **I found a bug** or
  **I want to request a feature**.

  Create an [issue on the GitHub project page](https://github.com/t-mart/ItemVersion/issues).

  Pull requests are also warmly welcome!

## License

Copyright 2022 Tim Martin

Licensed under the GPLv3:
[https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html)
