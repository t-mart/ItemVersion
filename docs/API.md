
# API

Below are the main functions of the public API.

## `ItemVersion:getItemVersion`

Type:
`function(itemId: number, includeCommunityUpdates: bool | nil) -> {major: number, minor: number, patch: number, build: number} | nil`

Given an itemId, return the version in which the item was added to the game. The returned value is a
table with fields `major`, `minor`, `patch`, and `build` that describe that version. If the itemId
is not present in the database, return `nil`.

If the `includeCommunityUpdates` argument is truthy, community updates will be preferred over
ItemVersion's canonical database. These updates attempt to correct instances in which items have
versions that are earlier than when they were usable. For example, Marrowroot was first usable
during Shadowlands, but was actually added towards the end of Battle for Azeroth. If
`includeCommunityUpdates` is false, these updates will not be considered.

Examples:

- ```lua
  -- Morrowroot
  local version = ItemVersion.getItemVersion(168589, false)
  -- version = {major = 8, minor = 2, patch = 0, build = 30918}
  ```

- ```lua
  -- Morrowroot
  local version = ItemVersion.getItemVersion(168589, true)
  -- version = {major = 9, minor = 0, patch = 0, build = 0}
  ```

- ```lua
  local version = ItemVersion.getItemVersion(-1)
  -- version = nil
  ```

## `ItemVersion:getVersionExpac`

Type: `function({major: number}) -> { canonName: string, shortName: string } | nil`

Given a table with field `major` (such as the table given by `ItemVersion.getItemVersion`), return
a table for the expansion of the version. Has fields for `canonName` and `shortName`.

Examples:

- ```lua
  local expac = ItemVersion.getVersionExpac(ItemVersion.getVersionExpac(19019))
  -- expac = {canonName = "Classic", shortName = "Classic"}
  ```

- ```lua
  local expac = ItemVersion.getVersionExpac(ItemVersion.getVersionExpac(192466))
  -- expac = {canonName = "Shadowlands", shortName = "SL"}
  ```

- ```lua
  local expac = ItemVersion.getVersionExpac(ItemVersion.getVersionExpac(999999999))
  -- expac = nil
  ```
