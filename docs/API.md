
# API

## `ItemVersion.getItemVersion`

Type:
`function(itemId: number) -> {major: number, minor: number, patch: number, build: number} | nil`

Given an itemId, return the version in which the item was added to the game. Has fields for the
`major`, `minor`, `patch`, and `build` components of the version. If the itemId is not present in
the database, return `nil`.

Examples:

- ```lua
  -- Thunderfury, Blessed Blade of the Windseeker
  local version = ItemVersion.getItemVersion(19019)
  -- version = {major = 1, minor = 11, patch = 1, build = 5462}
  ```

- ```lua
  local version = ItemVersion.getItemVersion(999999999)
  -- version = nil
  ```

## `ItemVersion.getVersionExpac`

Type: `function({major: number}) -> { canonName: string, shortName: string } | nil`

Given a table with field `major` (such as the table given by `ItemVersion.getItemVersion`), return
the expansion of the version. Has fields for `canonName` and `shortName`.

Examples:

- ```lua
  local expac = ItemVersion.getVersionExpac(ItemVersion.getVersionExpac(19019))
  -- expac = {canonName = "World of Warcraft", shortName = "WoW"}
  ```

- ```lua
  local expac = ItemVersion.getVersionExpac(ItemVersion.getVersionExpac(192466))
  -- expac = {canonName = "Shadowlands", shortName = "SL"}
  ```

- ```lua
  local expac = ItemVersion.getVersionExpac(ItemVersion.getVersionExpac(999999999))
  -- expac = nil
  ```

## `ItemVersion.buildVersionString`

Type: `function({major: number, minor: number, patch: number, build: number}) -> string`

Given a table with `major`, `minor`, `patch`, and `build` fields (such as the table given by
`ItemVersion.getItemVersion`), return a dot-separated string representation of that version.

Examples:

- ```lua
  local version = ItemVersion.buildVersionString(ItemVersion.getVersionExpac(19019))
  -- version = "1.11.1.5462"
  ```

## `ItemVersion.version`

Type: `number`

The currently installed version of ItemVersion. (Like the version of this addon, not of any
particular item.)

Examples:

- ```lua
  local addonVersion = ItemVersion.version
  -- addonVersion = 2022.17.0
  ```