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

## Release Process

See the GitHub Actions in this project. Essentially, releases happen:

- Automatically every week on Tuesday, in which the item database will be refreshed.
- Manually, whenever needed.
