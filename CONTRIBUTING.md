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
- `test` and `check` want [busted](https://lunarmodules.github.io/busted/) on a
  Lua 5.1 rock tree, to run the addon's Lua suite (see Running the Tests below).
- `prepare-src` and `build` want [Subversion](https://subversion.apache.org/), used
  to fetch the embedded Ace3 libraries from CurseForge.
- `publish` wants the [GitHub CLI](https://cli.github.com/) to create a release,
  and a `CURSEFORGE_TOKEN` (see `.env.template`) to upload to CurseForge.

### Running the Tests

There are two automated suites:

- `./dev test` runs the addon's Lua suite with
  [busted](https://lunarmodules.github.io/busted/). The specs live in `tests/` and
  exercise the addon's pure logic (the version lookup, corrections, token
  formatting, colors) outside the WoW client: a small harness in `tests/helper.lua`
  stubs the few globals the core touches and loads the addon files the way WoW
  would. It runs under PUC-Rio Lua 5.1, the version WoW ships, so 5.1-only
  behavior is what gets tested. Install busted on a Lua 5.1 rock tree first:

  ```bash
  luarocks --lua-version 5.1 install busted
  ```

  On Arch, the `lua51-busted` package works too and lands on your `PATH`.

- `./dev test-tooling` runs the Python tests for the `./dev` tooling itself
  (pytest, via uv). More esoteric; most contributors will not need it.

`./dev check` runs the Lua suite alongside the linters, formatter check, and
locale check, and `./dev watch` re-runs `check` on every save.

The busted suite cannot reach the parts that only exist inside the client (the
tooltip hook firing, client globals per flavor). Those are covered by a small
in-client suite in `src/ItemVersion/DevTests.lua`: install the addon into a flavor
(see below), then run `/ivtest` in game to print pass/fail for each client check.
That file is development-only. It is listed under `dev-only` in `wowaddon.yml`, so
`./dev build` drops it and strips its line from the packaged TOC; it loads only in
a symlinked dev install, never in a shipped release.

### Testing Your Changes In-Game

After you've made changes, you'll want to see how they behave in-game. The
recommended way to achieve this is as follows:

1. Generate the addon's non-committed pieces: the embedded libraries (fetched
   into `src/ItemVersion/Libs` with Subversion) and the locale files (generated
   from `src/translations.yml` into `src/ItemVersion/Locales`). Both are
   gitignored, and one command produces them:

   ```bash
   ./dev prepare-src
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

   To test the exact files that get published rather than your working tree, pass
   a source instead of the default symlink:

   - `./dev install --gh <tag>` copies a published GitHub release (use `latest`
     for the most recent one).
   - `./dev install --cf <file-id>` copies a published CurseForge file by id.

   These land as real directories, each carrying a `.dev-install` marker so
   `install-status` names them, `uninstall` cleans them up, and re-installing
   replaces them. A foreign directory sitting at the target is left alone unless
   you pass `--force`, which deletes it first.

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

The English text between the brackets is the key. That is all you have to write
in code: you do not touch any locale file. Once the string is in place, run:

```bash
./dev locales
```

This scans the code, adds an entry for your new key to
[`src/translations.yml`](https://github.com/t-mart/ItemVersion/blob/master/src/translations.yml),
and drops any entry no code uses anymore. The `check` command runs the same scan
without writing, and fails if the file is out of sync, which is what CI does.

`translations.yml` is the one place every string lives. Each entry is a key, an
optional `description` to help translators, and a translation per language:

```yaml
- key: Hello world
  description: Greeting shown on login.
  translations:
    deDE: Hallo Welt
```

A key with no `enUS` translation shows its own text to English players, which is
how AceLocale spells "this string is already English", so you rarely write an
`enUS` line at all. A language with no translation for a key falls back to that
English. The locale files under `src/ItemVersion/Locales/` are generated from
this file by `./dev prepare-src`; they are gitignored and never edited by hand.

There's nothing else to do. Translations live in this repo, so there is no
separate system to notify.

#### When one English word means two things

If the same English string is used in two places that a translator might want to
word differently, give each one a context, with `|` between the string and the
context. In code you look them up as `L["Legion|canon"]` and `L["Legion|short"]`,
and in `translations.yml` you spell out the English for each:

```yaml
- key: Legion|canon
  description: The expansion's full name.
  translations:
    enUS: Legion
- key: Legion|short
  description: The short form, for tight tooltip space.
  translations:
    enUS: Legion
```

Both are "Legion" in English, but one is the expansion's full name and the other
has to fit in a tooltip, and a language may want those to differ. Such a key
**needs** its `enUS` spelled out: without it, English players would see the
`|canon` marker itself. `check` enforces this.

### Translations

See
[Translators Needed](https://github.com/t-mart/ItemVersion/blob/master/README.md#translators-needed)
in the README. Editing the single `src/translations.yml` file is the whole
process, and no Lua knowledge is needed.

The `locales` command keeps that file tidy: it sorts entries by key, adds keys
the code has started using, and drops keys it has stopped using. `check` runs the
same checks without writing anything, which is what CI does. `prepare-src` then turns
the file into the Lua locale files the game loads.

## Building a Release

To create a packaged addon zip in `dist/`:

```bash
./dev build
```

This runs `prepare-src` (fetching libraries and generating the locale files), copies
`src/ItemVersion/` into `dist/`, stamps the build date into the TOC, and zips it
up. Files listed under `ignore` in `wowaddon.yml` (such as the development-only
`Bindings.xml`) are left out. Subversion needs to be installed for the library
fetch.

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

This is the format: `{YYYY}.{0W}.{N}`: the ISO week-year, the zero-padded ISO
week, and a 0-based serial. Releases in a new week reset the serial to 0;
releases within the same week increment it (0, 1, 2, ...).

`./dev bump-calver` computes the next version from today's date and rewrites the
`## Version:` line in the TOC, which is the single source of truth. Run it with
`--dry-run` to preview. The `version:` block in `wowaddon.yml` configures the
file, pattern and format; the bump does no git of its own.

## Release Process

See the
[`Release`](https://github.com/t-mart/ItemVersion/blob/master/.github/workflows/release.yml)
GitHub Action for details.

Releases happen in the following circumstances:

- Automatically every week on Tuesday, in which the item database will be
  refreshed.
- Manually, whenever a reasonable amount of development work warrants one.
