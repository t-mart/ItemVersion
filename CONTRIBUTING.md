# Contributing

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
- This addon uses [StyLua] for Lua code formatting. See its documentation for
  how to apply it to your contributions.

## Developer Environment

**Update: I know `wap` is crusty now. Talk to me if you can't get it working.**

ItemVersion uses [`wap`](https://t-mart.github.io/wap/) for most development
tasks. See
[wap for Collaborators](https://t-mart.github.io/wap/wap-for-collaborators/) to
get started. Using `wap` will give you a nice developer experience that
automatically rebuilds on file changes and links ItemVersion into your
`Interface/AddOns` directory.

In particular, if you do not use `wap` to build the addon, you won't be able to
use it in the game. This is because `wap` transforms the source files here into
a usable addon.

_(If you really don't want to use `wap`, you can just download the built addon
artifact that is created after each pull request by the `Build` workflow. But,
you'll only be able to access it after a one-time grant by me, and further, only
after you push. If you need `wap` help, just ask me.)_

## Versioning

ItemVersion adheres to [CalVer](https://calver.org/) for its releases.

This is the format: `year.weeknumber.patch`.

Data refresh releases will bump the `year.weeknumber` part. Intraweek
development releases will bump the `patch` part.

## Release Process

See the
[`Release`](https://github.com/t-mart/ItemVersion/blob/master/.github/workflows/release.yml)
GitHub Action for details.

Releases happen in the following circumstances:

- Automatically every week on Tuesday, in which the item database will be
  refreshed.
- Manually, whenever a reasonable amount of development work warrants one.
