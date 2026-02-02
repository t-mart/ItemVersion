# API

Below are the main functions of the public API.

## `ItemVersion.API.GetItemVersion`

**Type:**

```lua
function(itemId: number, applyVersionCorrections: bool | nil) -> ItemVersionLookup | nil
```

Where `ItemVersionLookup` is a table with the following fields and methods:

**Fields:**
- **`expansion`**: The expansion table containing:
  - `major`: The major version number (expansion number)
  - `canonName`: The full expansion name (e.g., "Shadowlands")
  - `shortName`: The abbreviated expansion name (e.g., "SL")
- **`minor`**: The minor version number
- **`patch`**: The patch version number
- **`build`**: The build number
- **`isCorrected`**: Boolean indicating whether this result came from version
  corrections

**Methods:**
- **`Format(formatString)`**: Formats a string by replacing tokens with values from this lookup (see below)

**Description:**

Given an `itemId`, return the version in which the item was added to the game.
If the `itemId` is not present in the database, return `nil`.

The returned lookup object contains version information fields and provides
methods for formatting the data

**Version Corrections:**

If the `applyVersionCorrections` argument is `true`, version corrections will be
checked first before consulting ItemVersion's canonical database. These
corrections handle cases where items were added to the game in an earlier
expansion but were not usable until a later expansion.

For example, Marrowroot (168589) was technically added during Battle for Azeroth
but wasn't usable until Shadowlands. With corrections enabled, it will show as
Shadowlands. With corrections disabled, it will show its canonical BfA version.

**Examples:**

```lua
-- Marrowroot without corrections (canonical version)
local version = ItemVersion.API.GetItemVersion(168589, false)
-- Returns:
-- {
--   expansion = { major = 8, canonName = "Battle for Azeroth", shortName = "BfA" },
--   minor = 2,
--   patch = 0,
--   build = 30918,
--   isCorrected = false
-- }
print(format("%d.%d.%d", version.expansion.major, version.minor, version.patch)) -- "8.2.0"
```

```lua
-- Marrowroot with corrections (usable version)
local version = ItemVersion.API.GetItemVersion(168589, true)
-- Returns:
-- {
--   expansion = { major = 9, canonName = "Shadowlands", shortName = "SL" },
--   minor = 0,
--   patch = 0,
--   build = 0,
--   isCorrected = true
-- }
print(version.expansion.canonName)           -- "Shadowlands"
```

```lua
-- Non-existent item
local version = ItemVersion.API.GetItemVersion(-1)
-- version = nil
```

## `ItemVersionLookup:Format`

**Type:**

```lua
method(formatString: string) -> string
```

**Description:**

Formats a string by replacing tokens with values from the lookup object.

This is a method available on `ItemVersionLookup` objects returned by `GetItemVersion`.

**Parameters:**

- **`formatString`**: A string containing tokens like `{expacLong}`, `{versionTriple}`, etc. that will be replaced with actual values from this lookup

**Returns:**

A formatted string with all tokens replaced by their corresponding values from the lookup data.

**Example:**

```lua
local version = ItemVersion.API.GetItemVersion(168589, true)
if version then
  local formatted = version:Format("Added in {expacLong} ({versionTriple})")
  print(formatted)  -- "Added in Shadowlands (9.0.0)"
end
```
