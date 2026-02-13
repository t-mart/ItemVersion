# ItemVersion Changelog

> [!NOTE]
> If a release is not documented here, it was likely an automated item database
> refresh.

## 2026.05.3

- Started this changelog.
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
