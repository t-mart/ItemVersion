# <img src="https://raw.githubusercontent.com/t-mart/ItemVersion/master/docs/images/icon.png" alt="Icon of a silver armored gauntlet with a blue glow" style="max-height: 1em;"> ItemVersion

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/t-mart/ItemVersion)](https://github.com/t-mart/ItemVersion/releases)
[![GitHub issues](https://img.shields.io/github/issues/t-mart/ItemVersion)](https://github.com/t-mart/ItemVersion/issues)
[![Hosted on Curseforge](https://img.shields.io/badge/hosted%20on-CurseForge-F16436)](https://www.curseforge.com/wow/addons/itemversion)

![Hero](https://raw.githubusercontent.com/t-mart/ItemVersion/master/docs/images/hero.png)

**ItemVersion adds information to your tooltip about when an item was added to
World of Warcraft.**

## Useful for

- Clearing your bags and bank of old stuff
- Identifying crafting reagents and loot from your transmog runs
- Looking back on WoW history

## Features

- A complete database of the version/expansion in which every item was added.
- Where-you-need-it accessibility in the item tooltip.
- Weekly updates with the latest items. A refreshed release will automatically
  occur (at least) every Tuesday at 16:00 UTC, just slightly after reset.
- [API](docs/API.md) exposed for use by other addons.
- Slash commands: Run `/itemversion help` to get started.

## Usage

Just install the addon like normal and mouse over any item!

![Demo of tooltip](https://raw.githubusercontent.com/t-mart/ItemVersion/master/docs/images/demo.png)

Access the options screen with `/itemversion`.

![Options screen](https://raw.githubusercontent.com/t-mart/ItemVersion/master/docs/images/options.png)

## API

See the
[API page](https://github.com/t-mart/ItemVersion/blob/master/docs/API.md)

## Contributing

- Beginners are welcome. If you are new to programming, Git, Lua, or anything
  related to the project, then I can help you. Just ask.
- No contribution is too small! Please submit as many fixes for typos and
  grammar bloopers as you can.
- Don't be afraid to open half-finished PRs, and ask questions if something is
  unclear!
- Pull requests should be made on their own separate branches.
- Try to limit each pull request to _one_ idea only.
- Please document how you tested your changes in your pull request.
- Make sure your changes pass the status checks.
- If you would like, please add your name to the
  [`AUTHORS.md`](https://github.com/t-mart/ItemVersion/blob/master/AUTHORS.md)
  file. Pseudonyms are fine.

See the
[Contributing document](https://github.com/t-mart/ItemVersion/blob/master/CONTRIBUTING.md)
for more information.

## Translators Needed

If you know another language, you can help, and you don't need to know how to
program.

The translations live in
[`ItemVersion/Locales/`](https://github.com/t-mart/ItemVersion/tree/master/ItemVersion/Locales),
one file per language. Open the one for yours, and you'll see lines like this:

```lua
L["Addon Version"] = "Versão do Addon"
-- L["Apply version corrections"] = ""
```

The first is translated. The second is commented out, which means nobody has
translated it yet: the English in the brackets is what a player sees today.
To translate it, delete the leading `-- ` and type your translation between the
empty quotes.

That's the whole job. You can do it in GitHub's web editor, using the pencil
icon on the file, and "Propose changes" will open a pull request for you.

Three things worth knowing:

- **Leave `enUS.lua` alone.** That one is the English source that everything
  else falls back to.
- **Keep anything in `%` or `{}` exactly as it is.** `%s`, `%d` and
  `{expacIcon}` get replaced with real values when the addon runs, so
  `"Added in {expacIcon}"` can become `"Added in Legion"`. You can move them
  around to suit your language, but don't rename or drop them.
- **Don't leave a line half done.** An empty `""` shows the player nothing at
  all, which is worse than English. If you want to skip one, comment it back
  out.

A missing language is fine too: just ask in an issue and one will be added.
Translations are living things, so if you spot one that reads badly, please say
so.

## Support

- **An item has the wrong version.**

  First, verify it on [wowhead.com](https://www.wowhead.com/).

  Note that, in some cases, items are added towards the end of an expansion that
  actually used in the _next_ expansion, making them appear to have too early of
  a version. For example,
  [Marrowroot](https://www.wowhead.com/item=168589/marrowroot), a herb used in
  Shadowlands, was actually added to the game during the previous expansion,
  Battle for Azeroth. And, ItemVersion will display Battle for Azeroth because
  it is canonically correct.

  However, to instead display the expansion that players probably expect in
  these cases, turn on the "Include community updates" option on the options
  screen. Then, the Marrowroot example would display Shadowlands.

  (These community updates are an ongoing effort. If you have discovered an item
  that feels like its in the wrong expansion, please lend a hand and create an
  [issue on the GitHub project page](https://github.com/t-mart/ItemVersion/issues)).

- **Anything else**

  Create an
  [issue on the GitHub project page](https://github.com/t-mart/ItemVersion/issues).

  Pull requests are also warmly welcome!

## License

Copyright 2026 Tim Martin

Licensed under the GPLv3:
[https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html)
