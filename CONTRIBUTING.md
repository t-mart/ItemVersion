# Contributing

## Pull Requests

- No contribution is too small! Please submit as many fixes for typos and grammar bloopers as you
  can!
- Don't be afraid to open half-finished PRs, and ask questions if something is unclear!
- PRs should be made on feature branches.
- Try to limit each pull request to _one_ change only.
- Please document how you tested your changes in your PR.
- Make sure your changes pass the status checks.
- If you would like, please add your name to the `AUTHORS` file. Pseudonyms are fine.

## Developer Environment

ItemVersion uses [wap](https://t-mart.github.io/wap/) for most development tasks.

## Versioning

ItemVersion adheres to [CalVer](https://calver.org/) for its releases.

This is the format: `year.weeknumber.patch`.

Data refresh releases will bump the `year.weeknumber` part. Intraweek development releases will bump
the `patch` part.

## Release Process

See the GitHub Actions in this project. Essentially, releases happen:

- Automatically every week on Tuesday, in which the item database will be refreshed.
- Manually, whenever needed.
