# Contributing Guidelines

- Beginners are welcome.
- Use LLMs to help you understand the codebase and development process. If that
  fails, ask your question in an issue or pull request.
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
  file. Usernames or pseudonyms are fine.

## Developing for ItemVersion

### Repo Setup

Clone the repository to a development location such as `~/code/ItemVersion`. Do
**not** clone directly into your `Interface/AddOns` directory, as this project's
structure differs from what WoW expects.

Once cloned, create a new branch off of `master` for your changes.

### Testing Your Changes In-Game

After you've made changes, you'll want to see how they behave in-game. The
recommended way to achieve this is as follows:

1. Download the addon dependencies in to `ItemVersion/Libs`. After putting the
   [BigWigs packager in your `PATH`](#bigwigs-packager), you can do this with
   the following command:

   ```bash
   make libs
   ```

2. Create a symbolic link from your development directory to your WoW
   `Interface/AddOns` directory. For example:

   ```bash
   ln -s ~/code/ItemVersion /path/to/WoW/Interface/AddOns/ItemVersion
   ```

   Or on Windows:

   ```cmd
   mklink /D C:\path\to\WoW\Interface\AddOns\ItemVersion C:\path\to\code\ItemVersion
   ```

3. Load the game up and try it out. Note that **whenever you make a change**,
   you must reload the UI in-game for it to take effect. You can do this by
   typing `/reload` in the chat.

> [!IMPORTANT]  
> Please test your changes before submitting a pull request and document thusly
> in your PR.

### Player-facing Strings

If you add any strings that are displayed to the player, make sure to perform a
lookup on the locale table. For example, instead of writing
`print("Hello world")`, you would write:

```lua
local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)

print(L["Hello world"])
```

Further, please list any new strings in your pull request. This is so I can add
them to
[the localization system](https://legacy.curseforge.com/wow/addons/itemversion/localization)
for later translation.

## BigWigs Packager

This project uses the
[BigWigs packager](https://github.com/BigWigsMods/packager) for building
releases.

To install it locally, place
[`release.sh`](https://github.com/BigWigsMods/packager/blob/master/release.sh)
somewhere in your `PATH`. Ask an LLM for help if you don't know how to do this.

## Building a Release

To create a packaged release build:

```bash
make build
```

This requires the [BigWigs packager to be installed locally](#bigwigs-packager).

Note that any replacements for `debug` will be omitted from the build.

## Versioning

ItemVersion adheres to [CalVer](https://calver.org/) for its releases.

This is the format: `year.weeknumber.patch`.

Data refresh releases will bump the `year.weeknumber` part. Intraweek
development releases will bump the `patch` part.

See `.bumpversion.toml` for more details.

## Release Process

See the
[`Release`](https://github.com/t-mart/ItemVersion/blob/master/.github/workflows/release.yml)
GitHub Action for details.

Releases happen in the following circumstances:

- Automatically every week on Tuesday, in which the item database will be
  refreshed.
- Manually, whenever a reasonable amount of development work warrants one.
