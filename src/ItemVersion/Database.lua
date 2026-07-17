local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)
local AceConsole = LibStub("AceConsole-3.0")

---@class DatabaseProfile
---@field enableTooltip boolean Whether to show version info in tooltips
---@field lineColor Color The color of the tooltip line
---@field showOnShift boolean Show tooltip when Shift is held
---@field showOnControl boolean Show tooltip when Control is held
---@field showOnAlt boolean Show tooltip when Alt is held
---@field showOnMeta boolean Show tooltip when Meta/Cmd is held (Mac only)
---@field applyCorrections boolean Whether to apply version corrections
---@field tooltipFormat string The format string for the tooltip
---@field version number The profile version number, stamped by migrate rather
---than defaulted

Private.DatabaseManager = {}
local Color = Private.Color

local NAME = "ItemVersionDB"
local CURRENT_VERSION_NUMBER = 2
local PRE_VERSIONED = 0

-- The shape of a profile at each schema version.
--
-- `version` is deliberately absent from all of these. AceDB rawsets defaults
-- into the profile before anything here can read it, and strips values equal to
-- their default on logout, so a defaulted version would always read as current
-- and would never survive a round trip. migrate stamps it explicitly instead,
-- which is what makes its absence mean something.
local VERSION_DEFAULTS = {
  -- back before versioning
  [PRE_VERSIONED] = {
    profile = {
      showPrefix = true,
      prefixColor = Color.White(),
      shortExpacNames = false,
      expacColor = Color.White(),
      showVersion = true,
      versionColor = Color.White(),
      showWhenMissing = false,
      showBuildNumber = true,
      keyModifiers = { shift = false, control = false, alt = false, meta = false },
      includeCommunityUpdates = true,
    },
  },
  [1] = {
    profile = {
      lineColor = Color.White(),
      showOnShift = false,
      showOnControl = false,
      showOnAlt = false,
      showOnMeta = false,
      applyCorrections = true,
      tooltipFormat = L["Added in {expacIcon} ({versionTriple})"],
    },
  },
  [2] = {
    profile = {
      enableTooltip = true,
      lineColor = Color.White(),
      showOnShift = false,
      showOnControl = false,
      showOnAlt = false,
      showOnMeta = false,
      applyCorrections = true,
      tooltipFormat = L["Added in {expacIcon} ({versionTriple})"],
    },
  },
}

local CURRENT_VERSION_DEFAULTS = VERSION_DEFAULTS[CURRENT_VERSION_NUMBER]

-- Pre-versioning keyModifiers subkey -> the v1 key it became.
local MODIFIER_MAP = {
  shift = "showOnShift",
  control = "showOnControl",
  alt = "showOnAlt",
  meta = "showOnMeta",
}

---Returns value unless it is nil, in which case fallback. Unlike `or`, this
---keeps a stored false.
---@generic T
---@param value T|nil
---@param fallback T
---@return T
local function valueOr(value, fallback)
  if value == nil then
    return fallback
  end

  return value
end

---Chooses between a value the user may have set since the overhaul and one
---carried from a pre-versioning profile. The newer value wins unless it is still
---sitting at its default, in which case the older preference fills the gap.
---
---A value explicitly set to its own default cannot be told apart from an
---untouched one, since AceDB strips both on logout. That costs nothing here:
---the two agree by definition.
---@generic T
---@param current T The value in the profile now
---@param currentDefault T What that value defaults to
---@param carried T The value mapped from the pre-versioning profile
---@return T
local function preferNewer(current, currentDefault, carried)
  if current ~= currentDefault then
    return current
  end

  return carried
end

---Reports whether a profile holds any key belonging to a schema shape
---@param profile table The profile to inspect
---@param shape table A schema's profile defaults, read for its keys
---@return boolean
local function hasAnyKeyOf(profile, shape)
  for key in pairs(shape) do
    if profile[key] ~= nil then
      return true
    end
  end

  return false
end

---Determines which schema version a profile is written in
---
---An absent version is ambiguous three ways. It means pre-versioning; or v1,
---whose version equalled its default and so was stripped on logout; or a
---profile created moments ago. Pre-versioning is told apart by its keys, none
---of which survive into a later schema.
---
---The remaining ambiguity between v1 and brand new is harmless: a profile is
---only indistinguishable from a new one when every value it held equalled a
---default, and every migration below maps defaults to defaults.
---@param profile table The profile to inspect
---@return number version
local function detectVersion(profile)
  local stamped = profile.version
  if stamped ~= nil then
    return stamped
  end

  if hasAnyKeyOf(profile, VERSION_DEFAULTS[PRE_VERSIONED].profile) then
    return PRE_VERSIONED
  end

  return 1
end

---Migrates a database profile to the current version
---@param database table The AceDB database object
local function migrate(database)
  local profile = database.profile
  local version = detectVersion(profile)

  if version == PRE_VERSIONED then
    local defaults = VERSION_DEFAULTS[PRE_VERSIONED].profile
    local target_defaults = VERSION_DEFAULTS[1].profile

    -- The overhaul shipped without a working migration, so a pre-versioning
    -- profile can also hold v1 values the user has set in the months since.
    -- Those are the more recent intent and win; the carried value only fills a
    -- setting still sitting at its default.
    --
    -- An absent key on either side means that side's default rather than
    -- "unset", since AceDB stripped whatever equalled it.
    local modifiers = valueOr(profile.keyModifiers, defaults.keyModifiers)

    for oldKey, newKey in pairs(MODIFIER_MAP) do
      local carried = valueOr(modifiers[oldKey], defaults.keyModifiers[oldKey])
      profile[newKey] = preferNewer(profile[newKey], target_defaults[newKey], carried)
    end

    profile.applyCorrections = preferNewer(
      profile.applyCorrections,
      target_defaults.applyCorrections,
      valueOr(profile.includeCommunityUpdates, defaults.includeCommunityUpdates)
    )

    -- lineColor and tooltipFormat are left alone. Pre-versioning had three
    -- separate colors and no format string, so there is nothing to carry, and
    -- AceDB has already supplied the default for anyone who set neither.
    Private.Table.KeepOnlyKnownKeys(profile, target_defaults)
    version = 1
  end

  if version == 1 then
    local target_defaults = VERSION_DEFAULTS[2].profile
    profile.enableTooltip = target_defaults.enableTooltip
    Private.Table.KeepOnlyKnownKeys(profile, target_defaults)
    version = 2
  end

  -- if version == 2 then
  --   -- future migrations would go here
  -- end

  -- Whatever is left is a version with no migration into the current schema,
  -- which in practice means a newer ItemVersion wrote the profile and the user
  -- has since downgraded. Their settings are lost either way: the keys of a
  -- schema we do not know cannot be carried anywhere. Resetting at least leaves
  -- a working addon, where raising here aborted OnInitialize and left every
  -- later step, including the tooltip hook, unrun.
  if version ~= CURRENT_VERSION_NUMBER then
    AceConsole:Print(
      format(L["ItemVersion does not support profile version %d, so your settings have been reset."], version)
    )

    -- Suppress callbacks, since OnProfileReset is wired to migrate. The nested
    -- pass would terminate, a reset profile reading as v1, but only by luck.
    -- ResetProfile empties the profile table rather than replacing it, so the
    -- local above still points at the live one.
    database:ResetProfile(nil, true)
    version = CURRENT_VERSION_NUMBER
  end

  -- Stamped last: the migrations above strip unknown keys, and version is not
  -- one any schema claims.
  profile.version = version
end

---Initialize the database and apply migrations
---@return table database The initialized AceDB database
function Private.DatabaseManager.Initialize()
  if Private.Database then
    return Private.Database
  end

  local database = LibStub("AceDB-3.0"):New(NAME, CURRENT_VERSION_DEFAULTS, true)

  migrate(database)

  Private.Database = database

  -- when profile changes, migrate to ensure schema
  ---@param _ string
  ---@param db table
  local function migrateCallback(_, db)
    migrate(db)
  end
  database.RegisterCallback(Private.Database, "OnProfileChanged", migrateCallback)
  database.RegisterCallback(Private.Database, "OnProfileCopied", migrateCallback)
  database.RegisterCallback(Private.Database, "OnProfileReset", migrateCallback)

  -- return in case caller wants it, but by and large, use Private.Database for access
  return database
end

---Get the AceDBOptions table for profile management
---@return table options The profile options table
function Private.DatabaseManager.GetProfileOptionsTable()
  return LibStub("AceDBOptions-3.0"):GetOptionsTable(Private.Database)
end
