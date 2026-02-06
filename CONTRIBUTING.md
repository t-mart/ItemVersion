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

## Developer Operations

`make build` will perform a one-time build of the addon, placing the result in
the `.release/ItemVersion` directory. This requires
[BigWigs packager's `release.sh`](https://github.com/BigWigsMods/packager) to be
in your `PATH`.

Run `make dev` to automatically build the addon whenever a source file changes.
This additionally requires [watchexec](https://github.com/watchexec/watchexec)
to be installed.

These commands become even more powerful if you soft-link the
`.release/ItemVersion` directory to your WoW AddOns directory, so that the built
addon is immediately available in-game after you reload the UI.

Commits on PRs will trigger a workflow that builds the addon.

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
