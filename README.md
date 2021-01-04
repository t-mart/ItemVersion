# ItemVersion

![Montage](https://i.imgur.com/LJRzR5Q.png)

**ItemVersion adds information to your tooltip about when an item was added to World of Warcraft.**

## Useful for

- Clearing your bags and bank of old stuff
- Identifying gear from your transmog runs
- Looking back on WoW history

## Features

- A complete database of when every item was added to the game, including `major.minor.patch.build`
version and expansion, such as `Version: 9.0.1.36216, Expac: Shadowlands`.
- Where-you-need-it accesiblity in the item tooltip.
- A queriable library for retrieving this information for other addons. (Docs coming soon.)
- Weekly updates with the latest items.
- Open source visibility.

## Usage

Just install the addon like normal and mouse over any item! More configuration may be available in
the future.

## Versioning/Updates

ItemVersion follows the [CalVer](https://calver.org/) versioning convention.

This is the format: `year.weeknumber.patch`.

Every week (on Tuesday at 16:00 UTC), a data refresh occurs and the date parts of the version will
be bumped and released to CurseForge. Intraweek development releases will bump the patch part of the
version.

## See a problem? Want a feature?

- Found an item you think is incorrectly versioned? Verify it
[wowhead.com](https://www.wowhead.com/). Unfortunately, you will find that ItemVersion is more often
than not correct about its claims. One area this is noticeable in is items added towards the end of
an expansion that are actually used in the _next_ expansion. Don't blame me -- blame the devs!
- Is an item missing?
- Still have an issue or want to request a feature? Create an issue on the
[GitHub project page](https://github.com/t-mart/ItemVersion/issues)
- Or fork the project and make a [pull request](https://github.com/t-mart/ItemVersion/pulls)!
