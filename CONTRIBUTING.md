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

### Tools

Everything is driven by one executable in the repo root:

```bash
./dev help
```

It needs [uv](https://docs.astral.sh/uv/getting-started/installation/), and
nothing else. A shebang hands the script to uv, which fetches the right Python
and the dependencies on first run, so there is no virtualenv to create or
activate. On Windows, where a shebang means nothing, run `uv run --script dev`
instead.

Some individual commands want a tool on your `PATH`, and each one tells you if
something it needs is missing:

- `check` and `format` want [selene](https://kampfkarren.github.io/selene/) and
  [stylua](https://github.com/JohnnyMorganz/StyLua).
- `libs` and `build` want [Subversion](https://subversion.apache.org/), used to
  fetch the embedded Ace3 libraries from CurseForge.
- `publish` wants the [GitHub CLI](https://cli.github.com/) to create a release,
  and a `CURSEFORGE_TOKEN` (see `.env.template`) to upload to CurseForge.

### Testing Your Changes In-Game

After you've made changes, you'll want to see how they behave in-game. The
recommended way to achieve this is as follows:

1. Download the addon dependencies in to `src/ItemVersion/Libs`. With Subversion
   installed, you can do this with the following command:

   ```bash
   ./dev libs
   ```

2. Tell the tooling where WoW lives, by copying the template and editing it:

   ```bash
   cp .env.template .env
   ```

   Set `WOW_ROOT` to the directory that contains `_retail_`, `_classic_` and
   friends. `.env` is gitignored, so your path stays out of the repo.

3. Link the addon into every flavor you have installed:

   ```bash
   ./dev install
   ```

   This symlinks `src/ItemVersion/` into each flavor's `Interface/AddOns`, so your
   edits are live with no build step. It refuses to touch a real directory, so
   it will not eat a copy of ItemVersion you installed normally. Pass
   `--flavor` (repeatable, e.g. `./dev install --flavor retail`) to install into
   only some flavors instead of all of them. The `install-status` command shows
   what is linked, and `uninstall` removes the links again.

   On Windows, creating a symlink needs either Developer Mode turned on
   (Settings > System > For developers) or an Administrator terminal.

4. Load the game up and try it out. Note that **whenever you make a change**,
   you must reload the UI in-game for it to take effect. You can do this by
   typing `/reload` in the chat.

> [!IMPORTANT]
>
> Please test your changes before submitting a pull request and document thusly
> in your PR.

### Player-facing Strings

If you add any strings that are displayed to the player, make sure to state them
as a lookup on the locale table. For example, instead of writing
`print("Hello world")`, you would write:

```lua
local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)

print(L["Hello world"])
```

Then add the string to
[`src/ItemVersion/Locales/enUS.lua`](https://github.com/t-mart/ItemVersion/blob/master/src/ItemVersion/Locales/enUS.lua),
in alphabetical order:

```lua
L["Hello world"] = true
```

`true` means "the value is the key", which is how AceLocale spells "this string
is already English". You don't need to do anything for the other languages:

```bash
./dev locales
```

will add a commented stub for your new string to every locale file, ready for a
translator to fill in, and the `check` command will tell you if you forgot.

There's nothing else to do. Translations live in this repo, so there is no
separate system to notify.

#### When one English word means two things

If the same English string is used in two places that a translator might want to
word differently, give each one a context, with `|` between the string and the
context:

```lua
L["Legion|canon"] = "Legion"
L["Legion|short"] = "Legion"
```

Both are "Legion" in English, but one is the expansion's full name and the other
has to fit in a tooltip, and a language may want those to differ.

Note that such a key needs its English spelled out, as above, and **not**
`true`. `true` makes the value the key, so a language without a translation for
it would show the player `Legion|canon`, marker and all. `check` enforces this,
but it's easier to just remember.

### Translations

See
[Translators Needed](https://github.com/t-mart/ItemVersion/blob/master/README.md#translators-needed)
in the README. Editing one file under `src/ItemVersion/Locales/` is the whole
process, and no Lua knowledge is needed beyond the quotes.

The `locales` command maintains those files: it sorts them, stubs out anything
untranslated, and drops keys that no longer exist. It rewrites every locale
except `enUS.lua`, which is written by hand. `check` runs the same checks
without writing anything, which is what CI does.

## Building a Release

To create a packaged addon zip in `dist/`:

```bash
./dev build
```

This copies `src/ItemVersion/` into `dist/`, stamps the build date into the TOC, and
zips it up. Files listed under `ignore` in `wowaddon.yml` (such as the
development-only `Bindings.xml`) are left out. Missing libraries are fetched
first, so Subversion needs to be installed.

To ship a build, `./dev publish` uploads it to CurseForge and, for a full
release, creates a GitHub release. Run it with `--dry-run` first to see exactly
what would go where without uploading anything:

```bash
./dev build
./dev publish --dry-run
```

Alpha and beta builds go to CurseForge only: `./dev publish --type alpha`. The
release workflow does all of this on the release branch; you rarely need to
publish by hand.

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
