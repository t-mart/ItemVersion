# Contributing

First off, thank you for considering contributing to ItemVersion! It's people like _you_ who make it
such a great tool for everyone.

- No contribution is too small! Please submit as many fixes for typos and grammar bloopers as you
  can!
- Don't be afraid to open half-finished PRs, and ask questions if something is unclear!
- PRs should be made on feature branches.
- Try to limit each pull request to _one_ change only.
- Please document how you tested your changes in your PR.
- Make sure your changes pass the status checks.

## Formatting

Formatting should be done with the [LuaFormatter](https://github.com/Koihik/LuaFormatter) tool. The
configuration file for it is located at `.lua-format`. Unfortunately, there's no easy way to check
if PRs are well formatted. Perhaps I will run them routinely.

## Passing Checks

New commits are run through [luacheck](https://github.com/mpeterv/luacheck) in PR status checks.
This program catches a lot of common lua errors.

While you don't need to, you could run luacheck locally before you make your PR. That would be
faster than waiting for the CI checks to run.

## Testing Locally

On Windows, you can create a _junction_ (kinda like a symlink) from your development source
directory to your addons directory.

A script has been provided that does just that.

To run it, in Powershell, run the following

```pwsh
.\dev-install.ps1
```

Then, you can just edit the files in this development repository and they will be linked to the
Addons directory -- no more copy & pasting.

## Versioning

ItemVersion adheres to [CalVer](https://calver.org/) for its releases.

This is the format: `year.weeknumber.patch`.

Data refresh releases will bump the `year.weeknumber` part. Intraweek development releases will bump
the `patch` part.

To increment versions, we use [BumpVer](https://gitlab.com/mbarkhau/pycalver), which provides the
`bumpver` command. Its configuration file is located at `bumpver.toml`. **This file is the source of
truth for the current version.**

## Release Process

1. A stopping point is identified in development to make a release.

   (Weekly releases occur on Tuesday and refresh `ItemVersion/Data.lua`. Because these release are
   cut from the master branch, any unreleased code in master will also be included. This may or may
   not be intended. On one hand, it lowers the amount of updates users need to download. But on the
   other hand, the weekly releases are supposed to only be for the data updates. I'm not sure which
   one is best. Maybe we'll make a `dev` branch that merges into master for development sometime.)

2. On the master branch, this new version is incremented to with the `bumpver`.

   ```console
   $ bumpver update --patch
   ```

   This command increments the version in `bumpver.toml`, creates a commit with this change and
   indicative message, and finally tags that commit, using the new version as the tag name.

3. The new commit and tag are pushed to GitHub.

4. The [CI workflow](https://github.com/t-mart/wap/actions/workflows/ci.yml) is triggered, and
   because the git ref is a tag, additional deploy steps will be taken, such as publishing to
   CurseForge and creating a GitHub release asset.
