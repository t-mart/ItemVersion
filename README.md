# <img src="docs/images/icon.png" alt="Icon of a silver armored gauntlet with a blue glow" style="max-height: 1em;"> ItemVersion

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
- Identifying crafting reagents and loot from your transmog runs
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

![Demo of tooltip](https://raw.githubusercontent.com/t-mart/ItemVersion/master/docs/images/demo.png)

Access the options screen with `/itemversion`.

![Options screen](https://raw.githubusercontent.com/t-mart/ItemVersion/master/docs/images/options.png)

## API

See the [API page](https://github.com/t-mart/ItemVersion/blob/master/docs/API.md)

## Contributing

- Beginners are welcome. If you are new to programming, Git, Lua, or anything related to the
  project, then I can help you. Just ask.
- No contribution is too small! Please submit as many fixes for typos and grammar bloopers as you
  can.
- Don't be afraid to open half-finished PRs, and ask questions if something is unclear!
- Pull requests should be made on their own separate branches.
- Try to limit each pull request to _one_ idea only.
- Please document how you tested your changes in your pull request.
- Make sure your changes pass the status checks.
- If you would like, please add your name to the
  [`AUTHORS.md`](https://github.com/t-mart/ItemVersion/blob/master/AUTHORS.md) file. Pseudonyms are
  fine.

See the [Contributing document](https://github.com/t-mart/ItemVersion/blob/master/CONTRIBUTING.md)
for more information.

## Translators Needed

If you know another language and want to help translate ItemVersion, please
[check this out](https://github.com/t-mart/ItemVersion/tree/master/ItemVersion/Locales).

Translations are living things. If you see an improvement to make, don't hesitate to bring it up.

## Support

- **An item has the wrong version.**

  First, verify it on [wowhead.com](https://www.wowhead.com/).

  Note that, in some cases, items are added towards the end of an expansion that actually used in
  the _next_ expansion, making them appear to have too early of a version. For example,
  [Marrowroot](https://www.wowhead.com/item=168589/marrowroot), a herb used in Shadowlands, was
  actually added to the game during the previous expansion, Battle for Azeroth. And, ItemVersion
  will display Battle for Azeroth because it is canonically correct.

  However, to instead display the expansion that players probably expect in these cases, turn on the
  "Include community updates" option on the options screen. Then, the Marrowroot example would
  display Shadowlands.

  (These community updates are an ongoing effort. If you have discovered an item that feels like its
  in the wrong expansion, please lend a hand and create an [issue on the GitHub project
  page](https://github.com/t-mart/ItemVersion/issues).

- **An item still has the wrong version** or **An item is missing** or **I found a bug** or
  **I want to request a feature**.

  Create an [issue on the GitHub project page](https://github.com/t-mart/ItemVersion/issues).

  Pull requests are also warmly welcome!

## License

Copyright 2022 Tim Martin

Licensed under the GPLv3:
[https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html)
