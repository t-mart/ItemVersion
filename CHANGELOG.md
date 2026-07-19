# ItemVersion Changelog

This file documents the user-facing changes made to ItemVersion over time.

If a release is not documented here, it was likely generated automatically to
update the item database.

## Unreleased

- Add an `{itemId}` format token that renders the item's ID.
  Fixes [#126](https://github.com/t-mart/ItemVersion/issues/126)
- Fix the documentation and format token help referring to a `{expacLong}` token
  that does not exist. The token for the full expansion name has always been
  `{expacFull}`. A format string using `{expacLong}` rendered it literally
  rather than the expansion name.
- Add a button in the Format Tokens help table to add the token to the format
  string. Fixes [#121](https://github.com/t-mart/ItemVersion/issues/121)
- Add a button to reset the format string to its default value.

## 2026.28.1

- The item database now loads in a compact run-length-encoded form, cutting
  ItemVersion's memory use by roughly 6x (from about 10.5 MB to under 2 MB) and
  shrinking the data file loaded at startup. The information shown in tooltips
  is unchanged.
- Spanish (Mexico), Russian, Korean and Traditional Chinese are now translated,
  and every other supported language has a file waiting for a first translation.
  Thanks to [@reysonk](https://github.com/reysonk) for the Russian
  ([#106](https://github.com/t-mart/ItemVersion/issues/106)) and to
  [@HectorZaGa](https://github.com/HectorZaGa) for the Spanish
  ([#116](https://github.com/t-mart/ItemVersion/issues/116)).
- Translations now live in the addon's own repository rather than on CurseForge.
  If you speak a language ItemVersion does not cover yet, every string is in a
  single file, `src/translations.yml`, and GitHub's web editor is enough to send
  a fix. A string with no line for your language just falls back to English.
- The original game is now called "Classic", both in full and abbreviated,
  instead of "World of Warcraft" and "Vanilla". This is what Blizzard internally
  calls it.
- Fix translations never loading. Only German could ever apply. Every other
  language silently fell back to English, including the Chinese and Brazilian
  Portuguese translations that were already finished and waiting. Thanks to
  [@HectorZaGa](https://github.com/HectorZaGa) for spotting this
  ([#104](https://github.com/t-mart/ItemVersion/pull/104)).
- Show and hide the version line as you press and release your chosen modifier
  key, without having to move the mouse away and back. If you have not set a
  modifier key, nothing changes
  ([#110](https://github.com/t-mart/ItemVersion/issues/110)).
- Fix the tooltip line breaking when an expansion name contains a `%`. Depending
  on the character following it, the line either threw an error or silently
  rendered the wrong text. This only affected translated names, so it was
  invisible in English
  ([#109](https://github.com/t-mart/ItemVersion/issues/109)).
- Fix settings migration, which never ran. If you used ItemVersion before the
  2026.05.1 overhaul, your key modifier and version correction choices were
  silently ignored and replaced with defaults. They are now restored for any
  setting you have not since changed, and anything you did change is left as you
  set it. Long-obsolete settings are also cleared out of your saved variables
  ([#108](https://github.com/t-mart/ItemVersion/issues/108)).
- Fix an "Invalid font asset" error thrown when opening the options panel.
  Thanks to [@HectorZaGa](https://github.com/HectorZaGa) for the report and the
  fix ([#105](https://github.com/t-mart/ItemVersion/pull/105)).
- Fix the "Apply version corrections" option, which did nothing. It always
  appeared unchecked no matter what you set it to, and corrections were always
  applied. It now shows the real setting and turning it off takes effect
  ([#107](https://github.com/t-mart/ItemVersion/issues/107)).

## 2026.07.2

- Use more reliable method of determining expansion availability for showing
  previews on the options screen.

## 2026.07.0

- Use
  [CurseForge translations](https://legacy.curseforge.com/wow/addons/itemversion/localization).
  This lowers the barrier to entry for translators to make contributions.
- Make tooltip integration optional. This is useful if you are using ItemVersion
  as a data API.
- Support Anniversary flavor of the game.

## 2026.05.3

- Start this changelog.
- Use [Big Wigs packager](https://github.com/BigWigsMods/packager) for releases.

## 2026.05.1

- Instead of piecemeal toggling of expansion information, you can now define a
  format string for your tooltip line. Tokens in the format string are replaced
  with item expansion information. For example, a format string of
  `Added in {expacFull}` will render as "Added in Mists of Pandaria".

- In addition to many other string tokens, we now support expansion icons in the
  tooltip line. Use the `{expacIcon}` token to see it.

- The public API has been changed. See
  https://github.com/t-mart/ItemVersion/blob/master/docs/API.md for more
  information. Old consumers (if any exist?) will have breakages.

- The public API has been cleaned up to not leak internal functions (that are
  useless to consumers)

- New and simplified options screen. Also has a better preview section so you
  can see the effect of your configuration.

- Lots of internal refactoring and re-achitecting. Much more fluent Lua now (I
  hope!)

- Many translated strings are unfortunately no longer relevant. If you speak one
  of the affected languages, please don't hesitate to reach out. I can help you
  get started, or you can submit a PR. It is not difficult to contribute this
  way.

## Earlier releases

Earlier releases are not documented here. See the git history for more
information.
